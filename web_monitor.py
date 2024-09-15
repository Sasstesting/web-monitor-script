import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants from environment variables
URL = os.environ.get('PARKING_URL')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

def check_availability():
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Adjust this selector based on the actual page structure
        subscribe_button = soup.find('button', id='subscription-submit')
        
        if subscribe_button and not subscribe_button.get('disabled'):
            send_notification("Subscription available!", "A parking subscription is now available in Vendôme!")
            return True
        else:
            logger.info("No subscription available at this time.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching the parking page: {e}")
    except Exception as e:
        logger.error(f"Unexpected error checking availability: {e}")
    return False

def send_notification(title, message):
    payload = {
        "title": title,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        response.raise_for_status()
        logger.info(f"Notification sent: {title}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending notification: {e}")

def daily_job():
    if not check_availability():
        send_notification("Daily Update", "The script ran successfully today, but no parking spots became available.")

def run_scheduled_job():
    logger.info("Running scheduled availability check")
    check_availability()

def main():
    if not URL or not WEBHOOK_URL:
        logger.error("PARKING_URL or WEBHOOK_URL environment variables are not set")
        sys.exit(1)

    schedule.every().day.at("07:00").do(run_scheduled_job)
    schedule.every().day.at("11:59").do(run_scheduled_job)
    schedule.every().day.at("17:00").do(run_scheduled_job)
    schedule.every().day.at("23:00").do(run_scheduled_job)
    schedule.every().day.at("23:30").do(daily_job)

    logger.info("Script started. Running checks at scheduled times.")
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Sleep for 1 minute between checks
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(300)  # Sleep for 5 minutes if there's an error

if __name__ == "__main__":
    main()
