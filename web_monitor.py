import os
import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
from pytz import timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Configuration
URL = os.environ.get('TARGET_URL')
ELEMENT_ID = os.environ.get('ELEMENT_ID')
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 3600))

# Make webhook configuration
MAKE_WEBHOOK_URL = os.environ.get('MAKE_WEBHOOK_URL')

# Timezone configuration
FRANCE_TZ = timezone('Europe/Paris')

# New variables for daily summary
SUMMARY_TIME = FRANCE_TZ.localize(datetime.now().replace(hour=21, minute=41, second=0, microsecond=0)).time()
found_today = False
last_summary_date = FRANCE_TZ.localize(datetime.now()).date()

def check_webpage():
    global found_today
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        target_element = soup.find(id=ELEMENT_ID)
        
        if target_element:
            logging.info(f"Parking spot available! Element with ID '{ELEMENT_ID}' found!")
            send_make_notification("parking_available", f"Parking spot available! Element '{ELEMENT_ID}' found on {URL}")
            found_today = True
            return True
        else:
            logging.info(f"No parking spot available. Element with ID '{ELEMENT_ID}' not found. Will check again in {CHECK_INTERVAL} seconds.")
    except Exception as e:
        logging.error(f"Error checking webpage: {str(e)}")
    
    return False

def send_make_notification(event_type, message):
    payload = {
        "event_type": event_type,
        "message": message,
        "timestamp": datetime.now(FRANCE_TZ).isoformat()
    }
    try:
        response = requests.post(MAKE_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logging.info(f"Make notification sent successfully. Event type: {event_type}")
    except Exception as e:
        logging.error(f"Error sending Make notification: {str(e)}")

def check_and_send_daily_summary():
    global found_today, last_summary_date
    current_datetime = FRANCE_TZ.localize(datetime.now())
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    
    if current_date > last_summary_date and current_time >= SUMMARY_TIME:
        event_type = "daily_summary"
        if found_today:
            message = f"Daily Summary: Parking spot was available today ({current_date})."
        else:
            message = f"Daily Summary: No parking spot was available today ({current_date})."
        send_make_notification(event_type, message)
        
        found_today = False
        last_summary_date = current_date

def main():
    global found_today
    logging.info("Starting parking spot monitor script...")
    send_make_notification("script_start", "Parking spot monitor script has started.")
    while True:
        check_webpage()
        check_and_send_daily_summary()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
