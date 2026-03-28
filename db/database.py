import sqlite3
import uuid
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import get_config

def get_db_path():
    return get_config()["DB_PATH"]

def init_db():
    """Create tables if they don't exist"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            booking_type TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'confirmed',
            created_at TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    conn.commit()
    conn.close()

def upsert_customer(name, email, phone):
    """Insert or return existing customer by email"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("SELECT customer_id FROM customers WHERE email = ?", (email,))
    row = c.fetchone()
    if row:
        customer_id = row[0]
    else:
        customer_id = str(uuid.uuid4())[:8].upper()
        c.execute(
            "INSERT INTO customers (customer_id, name, email, phone, created_at) VALUES (?, ?, ?, ?, ?)",
            (customer_id, name, email, phone, datetime.now().isoformat())
        )
        conn.commit()
    conn.close()
    return customer_id

def create_booking(customer_id, booking_type, date, time):
    """Insert a booking record"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    booking_id = "GLW-" + str(uuid.uuid4())[:6].upper()
    c.execute(
        "INSERT INTO bookings (id, customer_id, booking_type, date, time, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (booking_id, customer_id, booking_type, date, time, "confirmed", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return booking_id

def get_all_bookings():
    """Return all bookings joined with customer info"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("""
        SELECT b.id, c.name, c.email, c.phone, b.booking_type, b.date, b.time, b.status, b.created_at
        FROM bookings b
        JOIN customers c ON b.customer_id = c.customer_id
        ORDER BY b.date DESC, b.time DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def update_booking_status(booking_id, status):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
    conn.commit()
    conn.close()

def get_booking_stats():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM bookings")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM bookings WHERE status = 'confirmed'")
    confirmed = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM customers")
    customers = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM bookings WHERE date = date('now')")
    today = c.fetchone()[0]
    conn.close()
    return {"total": total, "confirmed": confirmed, "customers": customers, "today": today}

# Auto-init on import
init_db()
