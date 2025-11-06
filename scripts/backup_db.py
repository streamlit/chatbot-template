import requests
import os
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='/app/.env') # Adjust path if .env is elsewhere

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = os.getenv("TELEGRAM_USER_ID")
DATABASE_PATH = "/app/hotel_os_bot.db" # Path to the database file inside the container

def send_db_backup():
    """Sends the SQLite database file to the authorized Telegram user."""
    if not all([TELEGRAM_BOT_TOKEN, AUTHORIZED_USER_ID]):
        print("Error: Bot token or user ID not configured.")
        return

    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file not found at {DATABASE_PATH}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"backup_hotel_os_{timestamp}.db"

    with open(DATABASE_PATH, 'rb') as db_file:
        files = {'document': (file_name, db_file)}
        data = {'chat_id': AUTHORIZED_USER_ID, 'caption': f'Daily database backup from {timestamp}'}
        
        try:
            response = requests.post(url, data=data, files=files)
            response.raise_for_for_status()
            print(f"Successfully sent database backup to user {AUTHORIZED_USER_ID}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending backup: {e}")

if __name__ == "__main__":
    print("Executing daily database backup...")
    send_db_backup()
