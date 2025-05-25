import json
import requests
import sys

CONFIG_FILE = "pushover.config.json"
PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"

def send_notification(message, title=None):
    """
    Sends a notification message using the Pushover API.

    Args:
        message (str): The message content to send.
        title (str, optional): The title of the notification. 
                               If None, uses default_title from config.
    """
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{CONFIG_FILE}' not found.")
        print(f"Please create it by copying 'pushover.config.example.json' to '{CONFIG_FILE}'")
        print("and fill in your Pushover user_key and api_token.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{CONFIG_FILE}'. Please check its syntax.")
        sys.exit(1)

    try:
        pushover_config = config["pushover"]
        message_settings = config["message_settings"]

        user_key = pushover_config["user_key"]
        api_token = pushover_config["api_token"]
        
        if title is None:
            notification_title = message_settings.get("default_title", "Notification") # Fallback default
        else:
            notification_title = title

        if not user_key or user_key == "YOUR_PUSHOVER_USER_KEY":
            print(f"Error: 'user_key' in '{CONFIG_FILE}' is not configured or is still the default placeholder.")
            sys.exit(1)
        if not api_token or api_token == "YOUR_PUSHOVER_APP_API_TOKEN":
            print(f"Error: 'api_token' in '{CONFIG_FILE}' is not configured or is still the default placeholder.")
            sys.exit(1)

    except KeyError as e:
        print(f"Error: Missing expected key {e} in '{CONFIG_FILE}'.")
        print(f"Please ensure '{CONFIG_FILE}' follows the structure of 'pushover.config.example.json'.")
        sys.exit(1)

    payload = {
        "token": api_token,
        "user": user_key,
        "message": message,
        "title": notification_title
        # Future enhancements:
        # "priority": 0, # Default priority
        # "sound": "pushover" # Default sound
    }

    try:
        response = requests.post(PUSHOVER_API_URL, data=payload, timeout=10)
        if response.status_code == 200:
            print("Notification sent successfully.")
        else:
            print(f"Error sending notification: {response.status_code} - {response.text}")
            try:
                # Attempt to parse JSON error from Pushover for more details
                errors = response.json().get("errors", [])
                if errors:
                    print("Details: " + ", ".join(errors))
            except json.JSONDecodeError:
                pass # No JSON in error response, text already printed
    except requests.exceptions.Timeout:
        print("Error sending notification: The request timed out.")
    except requests.exceptions.ConnectionError:
        print("Error sending notification: Could not connect to the Pushover API. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending notification: An unexpected error occurred with the request: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python notify_pushover.py \"Your message here\" [\"Optional Title\"]")
        print("Example: python notify_pushover.py \"Scraping complete.\"")
        print("Example: python notify_pushover.py \"Critical Alert!\" \"System Alert\"")
        sys.exit(1)

    message_arg = sys.argv[1]
    title_arg = None

    if len(sys.argv) > 2:
        title_arg = sys.argv[2]

    send_notification(message_arg, title_arg)
