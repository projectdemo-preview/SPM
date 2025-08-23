from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from models import Birthday, db
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import time
from flask import Flask


# Flask app setup for database access in this script
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration (like email settings)
db.init_app(app)

def send_birthday_emails():
    with app.app_context():  # Ensure database access
        print("Checking for birthdays today...")  # Debug statement
        today = datetime.now().date()  # Get today's date
        print(f"Today's date: {today}")  # Print today's date for debugging

        # Query for birthdays today
        birthdays_today = Birthday.query.filter(
            db.extract('month', Birthday.date_of_birth) == today.month,
            db.extract('day', Birthday.date_of_birth) == today.day
        ).all()

        print(f"Found {len(birthdays_today)} birthdays today.")  # Debug statement
        
        if not birthdays_today:
            print("No birthdays today.")  # Debug message if no birthdays
        else:
            # Log the details of each birthday found
            for birthday in birthdays_today:
                print(f"Sending email to {birthday.name} ({birthday.email})")

            # Loop through birthdays and send emails
            for birthday in birthdays_today:
                msg = MIMEMultipart()
                msg['From'] = Config.EMAIL_USER
                msg['To'] = birthday.email
                msg['Subject'] = birthday.subject or "Happy Birthday!"

                # Body of the email
                body = birthday.message or f"Happy Birthday, {birthday.name}!"
                msg.attach(MIMEText(body, 'plain'))

                try:
                    print(f"Sending email to {birthday.email}...")  # Debug message before sending
                    with SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT) as server:
                        server.starttls()
                        server.login(Config.EMAIL_USER, Config.EMAIL_PASS)
                        server.sendmail(Config.EMAIL_USER, Config.EMAIL_PASS, msg.as_string())
                    print(f"Birthday email sent to {birthday.email}")
                 # To delectt after sending 
                    db.session.delete(birthday)
                    db.session.commit()
                    print(f"Deleted birthday record for {birthday.name} after sending email.")

                except Exception as e:
                    print(f"Failed to send email to {birthday.email}: {e}")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(func=send_birthday_emails, trigger="interval", minutes=1)
 # Schedule it every minute for testing
scheduler.start()

# Ensure the scheduler shuts down when the script exits
atexit.register(lambda: shutdown_scheduler())

def shutdown_scheduler():
    try:
        if scheduler.running:  # Check if the scheduler is running before shutting it down
            scheduler.shutdown()
            print("Scheduler shut down.")
    except Exception as e:
        print(f"Error shutting down scheduler: {e}")

print("Birthday scheduler started and running...")

# Keep the script running to allow the scheduler to keep working
try:
    while True:
        time.sleep(1)  # Wait indefinitely to allow scheduler to run in the background
except (KeyboardInterrupt, SystemExit):
    shutdown_scheduler()  # Call the shutdown function on exit
    print("Script interrupted, shutting down.")
