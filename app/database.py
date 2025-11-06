
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func

from app.config import DATABASE_URL, get_logger

logger = get_logger(__name__)

# Define the database schema
Base = declarative_base()

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    customer_name = Column(String, nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    room_number = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

class PaymentSlip(Base):
    __tablename__ = 'payment_slips'
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, nullable=False)
    file_id = Column(String, nullable=False) # Telegram file_id
    slip_data = Column(Text) # OCR extracted data
    verified = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=func.now())

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, default='General')
    date = Column(DateTime, default=func.now())

# --- Database Engine and Session --- #
# The `check_same_thread=False` is needed only for SQLite.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get a DB session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    try:
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)

# --- CRUD Operations --- #

def find_booking_by_details(db, name: str, amount: float):
    """Finds an unpaid booking matching customer name and amount."""
    return db.query(Booking).filter(
        Booking.customer_name.ilike(f'%{name}%'),
        Booking.total_price == amount,
        Booking.is_paid == False
    ).first()

def mark_booking_as_paid(db, booking_id: int):
    """Marks a booking as paid."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.is_paid = True
        db.commit()
        return booking
    return None

def create_payment_slip_record(db, booking_id: int, file_id: str, slip_data: str):
    """Creates a record for a new payment slip."""
    slip = PaymentSlip(
        booking_id=booking_id,
        file_id=file_id,
        slip_data=slip_data,
        verified=True # Mark as verified since we found a matching booking
    )
    db.add(slip)
    db.commit()
    return slip

def get_daily_report_data(db, date: datetime.date):
    """Fetches data for the daily financial report."""
    start_of_day = datetime.datetime.combine(date, datetime.time.min)
    end_of_day = datetime.datetime.combine(date, datetime.time.max)

    income = db.query(func.sum(Booking.total_price)).filter(
        Booking.is_paid == True,
        Booking.created_at >= start_of_day,
        Booking.created_at <= end_of_day
    ).scalar() or 0.0

    expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.date >= start_of_day,
        Expense.date <= end_of_day
    ).scalar() or 0.0

    return {"income": income, "expenses": expenses, "net": income - expenses}
