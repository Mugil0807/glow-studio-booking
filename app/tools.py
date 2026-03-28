import json
import re
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.database import upsert_customer, create_booking
from app.email_sender import send_confirmation_email

def parse_booking_json(text):
    """Extract JSON booking payload from LLM response text"""
    match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            return None
    return None

def validate_booking_fields(data):
    """Returns (is_valid, error_message)"""
    # Force all values to strings to avoid type errors from LLM output
    data = {k: str(v) if v is not None else "" for k, v in data.items()}

    email = data.get("customer_email", "")
    if "@" not in email or "." not in email:
        return False, "Invalid email address format."

    phone = re.sub(r'\D', '', data.get("customer_phone", ""))
    if len(phone) < 10:
        return False, "Phone number must have at least 10 digits."

    date_str = data.get("preferred_date", "")
    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if booking_date < datetime.today().date():
            return False, "Booking date cannot be in the past."
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format."

    time_str = data.get("preferred_time", "")
    try:
        booking_time = datetime.strptime(time_str, "%H:%M").time()
        if not (datetime.strptime("09:00", "%H:%M").time() <= booking_time <= datetime.strptime("20:00", "%H:%M").time()):
            return False, "Appointments are available between 09:00 and 20:00."
    except ValueError:
        return False, "Time must be in HH:MM format (24h)."

    for field in ["customer_name", "service_type"]:
        if not data.get(field, "").strip():
            return False, f"Missing field: {field}."

    return True, ""

def process_confirmed_booking(data):
    """Save to DB, send email. Returns (booking_id, email_ok, email_msg)"""
    valid, err = validate_booking_fields(data)
    if not valid:
        return None, False, err

    customer_id = upsert_customer(
        name=data["customer_name"],
        email=data["customer_email"],
        phone=data["customer_phone"],
    )
    booking_id = create_booking(
        customer_id=customer_id,
        booking_type=data["service_type"],
        date=data["preferred_date"],
        time=data["preferred_time"],
    )
    email_ok, email_msg = send_confirmation_email(
        to_email=data["customer_email"],
        customer_name=data["customer_name"],
        booking_id=booking_id,
        service=data["service_type"],
        date=data["preferred_date"],
        time=data["preferred_time"],
    )
    return booking_id, email_ok, email_msg
