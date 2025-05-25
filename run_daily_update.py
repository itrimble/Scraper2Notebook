import subprocess
import datetime
import os
import sys
import logging

# Setup Logging
LOG_FILE = 'daily_update.log'
logging.basicConfig(filename=LOG_FILE, 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define the path to the notify_pushover.py script
# Assuming it's in the same directory as run_daily_update.py
NOTIFY_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notify_pushover.py")

def run_script(script_name):
    """
    Executes a given Python script and logs its output and success/failure.

    Args:
        script_name (str): The name of the Python script to execute.

    Returns:
        bool: True if the script executed successfully, False otherwise.
    """
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    logging.info(f"Starting script: {script_name} from path: {script_path}")
    try:
        if not os.path.exists(script_path):
            logging.error(f"Script not found: {script_path}")
            return False

        result = subprocess.run([sys.executable, script_path], 
                                capture_output=True, 
                                text=True, 
                                check=False,
                                timeout=600) # Added a 10-minute timeout for safety

        if result.stdout:
            logging.info(f"Output from {script_name}:\n{result.stdout}")
        if result.stderr:
            logging.warning(f"Errors from {script_name}:\n{result.stderr}")

        if result.returncode == 0:
            logging.info(f"Script {script_name} completed successfully.")
            return True
        else:
            logging.error(f"Script {script_name} failed with return code {result.returncode}.")
            logging.error(f"Failure details for {script_name} - STDOUT:\n{result.stdout}")
            logging.error(f"Failure details for {script_name} - STDERR:\n{result.stderr}")
            return False
    except FileNotFoundError:
        logging.error(f"Error: The script {script_name} (or Python interpreter {sys.executable}) was not found.")
        return False
    except subprocess.TimeoutExpired:
        logging.error(f"Error: Script {script_name} timed out after 10 minutes.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while running {script_name}: {e}")
        return False

def send_pushover_notification(message, title=None):
    """
    Sends a notification using the notify_pushover.py script.

    Args:
        message (str): The message content for the notification.
        title (str, optional): The title of the notification.
    """
    logging.info(f"Attempting to send Pushover notification: Title='{title}', Message='{message}'")
    
    if not os.path.exists(NOTIFY_SCRIPT_PATH):
        logging.error(f"Pushover notification script not found at: {NOTIFY_SCRIPT_PATH}")
        logging.error("Cannot send Pushover notification.")
        return

    cmd = [sys.executable, NOTIFY_SCRIPT_PATH, message]
    if title:
        cmd.append(title)

    try:
        result = subprocess.run(cmd, 
                                capture_output=True, 
                                text=True, 
                                check=False,
                                timeout=60) # 1 minute timeout for notification

        if result.returncode == 0:
            logging.info("Pushover notification request sent successfully.")
            if result.stdout:
                logging.info(f"Output from notify_pushover.py:\n{result.stdout}")
        else:
            logging.error(f"notify_pushover.py failed with return code {result.returncode}.")
            if result.stdout:
                logging.error(f"notify_pushover.py STDOUT:\n{result.stdout}")
            if result.stderr:
                logging.error(f"notify_pushover.py STDERR:\n{result.stderr}")
        
        # Further check stdout from notify_pushover.py for explicit success/error messages
        # This relies on notify_pushover.py printing "Notification sent successfully." or error messages.
        if "Notification sent successfully." not in result.stdout and result.returncode == 0:
             logging.warning(f"notify_pushover.py did not explicitly confirm success, but exited 0. Output: {result.stdout}")
        elif "Error" in result.stdout or "Error" in result.stderr: # Catch errors printed by the script itself
            logging.error(f"notify_pushover.py reported an error in its output even if it exited 0.")


    except subprocess.TimeoutExpired:
        logging.error("Error: notify_pushover.py timed out.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while running notify_pushover.py: {e}")

if __name__ == "__main__":
    logging.info("==================================================")
    logging.info("Starting daily RooCode data update process...")
    logging.info(f"Log file for this run: {LOG_FILE}")
    
    scrape_success = False
    ingest_success = False

    # Run scrape_reddit.py
    logging.info("--- Step 1: Running scrape_reddit.py ---")
    scrape_success = run_script("scrape_reddit.py")

    # Run ingest.py (conditionally)
    logging.info("--- Step 2: Running ingest.py (conditional) ---")
    if scrape_success:
        ingest_success = run_script("ingest.py")
    else:
        ingest_success = False # Ensure it's explicitly false if scrape failed
        logging.warning("Skipping ingest.py because scrape_reddit.py failed or was skipped.")

    # Determine Overall Status and Send Notification
    logging.info("--- Step 3: Determining Overall Status & Sending Notification ---")
    status_message = ""
    notification_title = ""
    
    if scrape_success and ingest_success:
        status_message = "Daily RooCode data update completed successfully."
        notification_title = "RooCode Update Success"
        logging.info(status_message)
        send_pushover_notification(status_message, notification_title)
    else:
        failure_reasons = []
        if not scrape_success:
            failure_reasons.append("scrape_reddit.py failed")
        
        # Only report ingest failure if scrape was successful but ingest failed
        if scrape_success and not ingest_success:
            failure_reasons.append("ingest.py failed")
        # Report ingest skipped if scrape failed (ingest_success is already False)
        elif not scrape_success: # Implies ingest was not run
            failure_reasons.append("ingest.py skipped due to scrape failure")
            
        if not failure_reasons: # Should not happen if we are in this else block, but as a fallback
            failure_reasons.append("an unknown error")

        status_message = f"Daily RooCode data update failed. Reasons: {', '.join(failure_reasons)}"
        notification_title = "RooCode Update FAILED"
        logging.error(status_message)
        send_pushover_notification(status_message, notification_title)

    logging.info("Daily RooCode data update process finished.")
    logging.info("==================================================")
