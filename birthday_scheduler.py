from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from models import Birthday, db
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import time
import re
from flask import Flask

# Flask app setup for database access in this script
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration (like email settings)
db.init_app(app)

# Helper function to validate email format
def is_valid_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None


def send_birthday_emails():
    with app.app_context():  # Ensure database access
        print("Checking for birthdays today...")
        today = datetime.now().date()
        print(f"Today's date: {today}")

        # Query for birthdays today
        birthdays_today = Birthday.query.filter(
            db.extract('month', Birthday.date_of_birth) == today.month,
            db.extract('day', Birthday.date_of_birth) == today.day
        ).all()

        print(f"Found {len(birthdays_today)} message to send  today.")

        for birthday in birthdays_today:
            # Validate email addresses
            if not is_valid_email(birthday.email) or not is_valid_email(birthday.user_email):
                print(f"Invalid email address: {birthday.email} or {birthday.user_email}")
                continue   ########

            print(f"Preparing to send email to {birthday.name} ({birthday.email})")
            msg = MIMEMultipart()
            msg['From'] = birthday.user_email
            msg['To'] = birthday.email
            msg['Subject'] = birthday.subject or "Happy Birthday!"
            
            # Body of the email
            body = birthday.message or f"Happy Birthday, {birthday.name}!"
            msg.attach(MIMEText(body, 'plain'))

            try:
                print(f"Sending email to {birthday.email}...")
                with SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT) as server:
                    server.starttls()
                    server.login(birthday.user_email, birthday.user_password)
                    server.sendmail(birthday.user_email, birthday.email, msg.as_string())
                print(f" Email sent to {birthday.email}")
                
                # Optional: Mark the record as processed
                db.session.delete(birthday)
                db.session.commit()
                print(f"Deleted  record for {birthday.name} after sending email.")

            except Exception as e:
                print(f"Failed to send email to {birthday.email}: {e}")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(func=send_birthday_emails, trigger="interval", minutes=1)  # Schedule every minute for testing
scheduler.start()

# Ensure the scheduler shuts down when the script exits
atexit.register(lambda: shutdown_scheduler())

def shutdown_scheduler():
    try:
        if scheduler.running:
            scheduler.shutdown()
            print("Scheduler shut down.")
    except Exception as e:
        print(f"Error shutting down scheduler: {e}")

print("Birthday scheduler started and running...")

# Keep the script running to allow the scheduler to keep working
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    shutdown_scheduler()
    print("Script interrupted, shutting down.")
