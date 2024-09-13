import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import time
import logging

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

def check_webpage():
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        target_element = soup.find(id=ELEMENT_ID)
        
        if target_element:
            logging.info(f"Element with ID '{ELEMENT_ID}' found!")
            send_email_notification()
            return True
        else:
            logging.info(f"Element with ID '{ELEMENT_ID}' not found. Will check again in {CHECK_INTERVAL} seconds.")
    except Exception as e:
        logging.error(f"Error checking webpage: {str(e)}")
    
    return False

def send_email_notification():
    subject = f"Element '{ELEMENT_ID}' Found on {URL}"
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

def main():
    logging.info("Starting webpage monitor script...")
    while True:
        if check_webpage():
            logging.info("Target element found. Script will continue to monitor.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
