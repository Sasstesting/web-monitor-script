import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import time
import logging
from datetime import datetime, time as dt_time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Configuration
URL = os.environ.get('TARGET_URL')
ELEMENT_ID = os.environ.get('ELEMENT_ID')
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 3600))

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')

# New variables for daily summary
SUMMARY_TIME = dt_time(21, 0)  # 9:00 PM
found_today = False
last_summary_date = datetime.now().date()

def check_webpage():
    global found_today
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        target_element = soup.find(id=ELEMENT_ID)
        
        if target_element:
            logging.info(f"Element with ID '{ELEMENT_ID}' found!")
            send_email_notification(f"Element '{ELEMENT_ID}' Found on {URL}")
            found_today = True
            return True
        else:
            logging.info(f"Element with ID '{ELEMENT_ID}' not found. Will check again in {CHECK_INTERVAL} seconds.")
    except Exception as e:
        logging.error(f"Error checking webpage: {str(e)}")
    
    return False

def send_email_notification(subject, body=None):
    if body is None:
        body = f"The element with ID '{ELEMENT_ID}' has been found on {URL}."
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        logging.info("Email notification sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")

def check_and_send_daily_summary():
    global found_today, last_summary_date
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    
    if current_date > last_summary_date and current_time >= SUMMARY_TIME:
        if not found_today:
            subject = f"Daily Summary: Element '{ELEMENT_ID}' Not Found"
            body = f"The element with ID '{ELEMENT_ID}' was not found on {URL} today ({current_date})."
            send_email_notification(subject, body)
        
        found_today = False
        last_summary_date = current_date

def main():
    global found_today
    logging.info("Starting webpage monitor script...")
    while True:
        check_webpage()
        check_and_send_daily_summary()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
