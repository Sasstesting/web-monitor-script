import requests
import os
from datetime import datetime

# The webhook URL from Make
MAKE_WEBHOOK_URL = os.environ.get('MAKE_WEBHOOK_URL')

def send_to_make(message):
    payload = {
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(MAKE_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"Successfully sent to Make. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Make: {e}")

if __name__ == "__main__":
    send_to_make("Hello from Python! This is a test message.")
