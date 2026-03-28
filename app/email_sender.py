import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import get_config

def send_confirmation_email(to_email, customer_name, booking_id, service, date, time):
    """Send a styled HTML confirmation email via Gmail SMTP"""
    cfg = get_config()
    gmail_user = cfg["GMAIL_USER"]
    gmail_pass = cfg["GMAIL_PASS"]
    salon_name = cfg["SALON_NAME"]

    if not gmail_user or not gmail_pass:
        return False, "Email credentials not configured."

    subject = f"✨ Booking Confirmed — {salon_name}"

    html_body = f"""
    <html><body style="font-family: Georgia, serif; background: #FAF7F2; padding: 40px;">
    <div style="max-width: 520px; margin: auto; background: white; border-radius: 4px; overflow: hidden; border: 1px solid #EDE8E3;">
        <div style="background: #2C2C2C; padding: 32px 40px; text-align: center;">
            <h1 style="color: #FAF7F2; font-size: 1.8rem; margin: 0; letter-spacing: 0.05em;">✨ {salon_name}</h1>
            <p style="color: #BFA07A; margin: 6px 0 0; font-size: 0.75rem; letter-spacing: 0.2em; text-transform: uppercase;">Booking Confirmation</p>
        </div>
        <div style="padding: 40px;">
            <p style="color: #2C2C2C; font-size: 1.05rem;">Dear <strong>{customer_name}</strong>,</p>
            <p style="color: #5C5C5C;">Your appointment has been confirmed. Here are your details:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 24px 0;">
                <tr style="border-bottom: 1px solid #EDE8E3;">
                    <td style="padding: 12px 0; color: #8A7F7A; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;">Booking ID</td>
                    <td style="padding: 12px 0; color: #2C2C2C; font-weight: 500;">{booking_id}</td>
                </tr>
                <tr style="border-bottom: 1px solid #EDE8E3;">
                    <td style="padding: 12px 0; color: #8A7F7A; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;">Service</td>
                    <td style="padding: 12px 0; color: #2C2C2C; font-weight: 500;">{service}</td>
                </tr>
                <tr style="border-bottom: 1px solid #EDE8E3;">
                    <td style="padding: 12px 0; color: #8A7F7A; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;">Date</td>
                    <td style="padding: 12px 0; color: #2C2C2C; font-weight: 500;">{date}</td>
                </tr>
                <tr>
                    <td style="padding: 12px 0; color: #8A7F7A; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;">Time</td>
                    <td style="padding: 12px 0; color: #2C2C2C; font-weight: 500;">{time}</td>
                </tr>
            </table>
            <p style="color: #5C5C5C; font-size: 0.9rem;">Please arrive 5 minutes early. To reschedule, reply to this email.</p>
            <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #EDE8E3; text-align: center; color: #8A7F7A; font-size: 0.8rem;">
                {salon_name} · Luxury Salon & Spa
            </div>
        </div>
    </div>
    </body></html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = gmail_user
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, to_email, msg.as_string())

        return True, "Email sent successfully."
    except Exception as e:
        return False, f"Email failed: {str(e)}"
