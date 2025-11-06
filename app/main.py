
import asyncio
import threading
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import google.generativeai as genai
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
import datetime
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

# Import from our modules
from app.config import (
    TELEGRAM_BOT_TOKEN, AUTHORIZED_USER_ID, GEMINI_API_KEY,
    get_logger
)
from app.database import init_db, get_db, find_booking_by_details, mark_booking_as_paid, create_payment_slip_record, get_daily_report_data
from app.ocr import process_payment_slip
from app.mqtt import publish_command
from geofence import get_geofences_containing_point

# --- Initialization ---
logger = get_logger(__name__)

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-pro')

# FastAPI app setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="webapp"), name="static")

# --- Authorization ---
def is_authorized(update: Update) -> bool:
    """Checks if the user is authorized to use the bot."""
    return update.effective_user.id == AUTHORIZED_USER_ID

# --- Telegram Bot Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    # Create a button that opens the web app
    web_app_button = KeyboardButton(
        "Open Hotel OS Web App",
        web_app=WebAppInfo(url=f"https://nssuwan186-Bot-telegram.hf.space/static/index.html")
    )
    keyboard = [[web_app_button]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Welcome to Hotel OS! Use the button below to manage payments and expenses.",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    help_text = """
    Available Commands:
    /start - Show the main menu and Web App button.
    /help - Show this help message.
    /daily_report - Get a summary of today's income and expenses.
    /light <ON|OFF> - Control the lights.
    /ac <ON|OFF|temperature> - Control the AC.
    
    You can also send me a payment slip image to verify it, or ask me anything else.
    """
    await update.message.reply_text(help_text)

async def daily_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    db = next(get_db())
    today = datetime.date.today()
    report_data = get_daily_report_data(db, today)
    message = (
        f"Financial Report for {today.strftime('%Y-%m-%d')}:\n"
        f"- Total Income: {report_data['income']:.2f} THB\n"
        f"- Total Expenses: {report_data['expenses']:.2f} THB\n"
        f"--------------------\n"
        f"- Net Profit: {report_data['net']:.2f} THB"
    )
    await update.message.reply_text(message)

async def handle_payment_slip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    
    file_id = update.message.photo[-1].file_id
    await update.message.reply_text("Processing your payment slip... This may take a moment.")

    ocr_result = await asyncio.to_thread(process_payment_slip, context.bot, file_id)

    if not ocr_result:
        await update.message.reply_text("Sorry, I couldn't read the details from the slip. Please check the image quality or enter the details manually.")
        return

    db = next(get_db())
    booking = find_booking_by_details(db, name=ocr_result['name'], amount=ocr_result['amount'])

    if booking:
        mark_booking_as_paid(db, booking.id)
        create_payment_slip_record(db, booking.id, file_id, str(ocr_result))
        await update.message.reply_text(
            f"Success! Payment verified for booking ID {booking.id} (Customer: {booking.customer_name}). The booking is now marked as paid."
        )
    else:
        await update.message.reply_text(
            f"I read the slip (Name: {ocr_result['name']}, Amount: {ocr_result['amount']}), but couldn't find a matching unpaid booking. Please check the details."
        )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    
    await update.message.reply_text(f"Received your location: Lat={lat}, Lon={lon}. Checking geofences...")

    db = next(get_db())
    containing_fences = get_geofences_containing_point(db, lat, lon)

    if containing_fences:
        fence_names = [f.name for f in containing_fences]
        await update.message.reply_text(f"You are currently inside the following geofence(s): {', '.join(fence_names)}")
    else:
        await update.message.reply_text("You are not currently inside any known geofence.")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    
    user_text = update.message.text
    logger.info(f"Received text from user: {user_text}")

    # Simple routing for hardware commands
    if user_text.lower().startswith('/light'):
        parts = user_text.split()
        if len(parts) > 1 and parts[1].upper() in ['ON', 'OFF']:
            command = parts[1].upper()
            if publish_command('light', command):
                await update.message.reply_text(f"Turned the light {command}.")
            else:
                await update.message.reply_text("Failed to send command to the light.")
        else:
            await update.message.reply_text("Usage: /light <ON|OFF>")
        return

    if user_text.lower().startswith('/ac'):
        parts = user_text.split()
        if len(parts) > 1:
            command = parts[1].upper()
            if publish_command('ac', command):
                await update.message.reply_text(f"Sent command '{command}' to the AC.")
            else:
                await update.message.reply_text("Failed to send command to the AC.")
        else:
            await update.message.reply_text("Usage: /ac <ON|OFF|temperature>")
        return

    # Fallback to Gemini AI
    await update.message.reply_chat_action('typing')
    try:
        response = await asyncio.to_thread(ai_model.generate_content, user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Error calling Gemini AI: {e}", exc_info=True)
        await update.message.reply_text("Sorry, I'm having trouble connecting to my AI brain. Please try again later.")

# --- FastAPI Endpoints ---
@app.get("/")
async def root():
    # This could be a simple health check page
    return {"status": "running"}

# --- Application Lifecycle ---
def run_bot():
    """Runs the Telegram bot in a polling loop."""
    logger.info("Starting Telegram bot polling...")
    bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("daily_report", daily_report_command))
    bot_app.add_handler(MessageHandler(filters.PHOTO, handle_payment_slip))
    bot_app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    bot_app.run_polling()

@app.on_event("startup")
async def startup_event():
    """Actions to take on application startup."""
    logger.info("Application startup...")
    init_db() # Initialize the database
    
    # Run the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Telegram bot thread started.")
