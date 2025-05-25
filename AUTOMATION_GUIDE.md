# Automating Daily Data Updates

This guide explains how to set up automated daily updates for the RooCode Data Query application. This process involves running the Reddit scraper (`scrape_reddit.py`) and the data ingestion script (`ingest.py`) automatically each day, with notifications sent via Pushover.

## Prerequisites

1.  **Python Environment:** Ensure your Python environment is set up as described in the main `README.md`.
2.  **Pushover Account:** You will need a Pushover account and your User Key, as well as an Application API Token.
3.  **Project Files:** You should have the latest project files, including `run_daily_update.py`, `notify_pushover.py`, `scrape_reddit.py`, `ingest.py`, and `pushover.config.example.json`.

## 1. Install Dependencies

If you haven't installed the `requests` library yet (it might have been added to `requirements.txt` recently), install it:

```bash
pip install requests
```
*(The main `requirements.txt` should ideally be updated to include `requests`)*

## 2. Configure Pushover Notifications

Follow these steps to set up Pushover:

1.  **Sign up or Log in:** Go to [https://pushover.net/](https://pushover.net/) and create an account or log in.
2.  **Find Your User Key:** Once logged in, your User Key is displayed on your dashboard. It's a long string of characters.
3.  **Register an Application:**
    *   Scroll down to the "Your Applications" section on your Pushover dashboard.
    *   Click on "Create an Application/API Token".
    *   Fill in the details:
        *   **Name:** Give your application a name (e.g., "RooCode Updater").
        *   **Type:** Select "Application".
        *   **Description:** Optional (e.g., "Notifications for RooCode data updates").
        *   **URL:** Optional.
        *   **Icon:** Optional.
    *   Check the box to agree to the terms and conditions.
    *   Click "Create Application".
4.  **Get Your API Token:** After creating the application, you'll be taken to its page. The API Token (e.g., `YOUR_PUSHOVER_APP_API_TOKEN`) will be displayed here.
5.  **Create `pushover.config.json`:**
    *   In the root directory of the project, make a copy of `pushover.config.example.json` and rename it to `pushover.config.json`.
    *   Open `pushover.config.json` with a text editor.
    *   Replace `"YOUR_PUSHOVER_USER_KEY"` with your actual User Key.
    *   Replace `"YOUR_PUSHOVER_APP_API_TOKEN"` with your actual Application API Token.
    *   It should look like this (with your actual keys):
      ```json
      {
          "pushover": {
              "user_key": "uQiXo...........YourUserKey...........",
              "api_token": "azGDO...........YourApiToken..........."
          },
          "message_settings": {
              "default_title": "RooCode Data Update"
          }
      }
      ```
6.  **Test (Optional but Recommended):**
    You can test your Pushover setup by running the notification script directly from your terminal:
    ```bash
    python notify_pushover.py "Test message from RooCode App" "Test Title"
    ```
    You should receive a Pushover notification on your configured devices. If not, double-check your keys in `pushover.config.json` and ensure `notify_pushover.py` is working correctly.

## 3. Schedule Daily Execution

The `run_daily_update.py` script is designed to orchestrate the update process. You need to schedule this script to run daily using your operating system's task scheduler.

**Important:**
*   Replace `/path/to/your/project/` with the actual absolute path to the root directory of this project on your computer in all the examples below.
*   Ensure that the Python executable used (`python` or `python3`) is the one associated with your project's environment where all dependencies are installed. You might need to use an absolute path to the Python executable if you have multiple Python versions (e.g., `/usr/bin/python3` or `/path/to/your/venv/bin/python`).

### For macOS or Linux (using `cron`):

1.  **Open your crontab for editing:**
    ```bash
    crontab -e
    ```
2.  **Add a new line to schedule the script.** For example, to run it every day at 3:00 AM:
    ```cron
    0 3 * * * /usr/bin/python3 /path/to/your/project/run_daily_update.py >> /path/to/your/project/cron_output.log 2>&1
    ```
    *   `0 3 * * *`: This means at minute 0 of hour 3, every day, every month, every day of the week. Adjust the time as needed.
    *   `/usr/bin/python3`: Path to your Python 3 executable. Verify this path.
    *   `/path/to/your/project/run_daily_update.py`: Absolute path to the script.
    *   `>> /path/to/your/project/cron_output.log 2>&1`: This redirects both standard output and standard error from the cron job to a log file named `cron_output.log` within your project directory. This is helpful for troubleshooting the cron job itself. The script `run_daily_update.py` also has its own logging to `daily_update.log`.

3.  **Save and exit the crontab editor.** Your system will automatically pick up the new schedule.

### For Windows (using Task Scheduler):

1.  **Open Task Scheduler:** Search for "Task Scheduler" in the Start Menu.
2.  **Create a Basic Task:**
    *   In the right-hand pane, click "Create Basic Task...".
    *   **Name:** Give it a name (e.g., "RooCode Daily Update").
    *   **Description:** (Optional) e.g., "Runs RooCode data scraping and ingestion daily."
    *   Click "Next".
3.  **Trigger:**
    *   Select "Daily".
    *   Click "Next".
    *   Set a start date and time (e.g., 3:00:00 AM).
    *   Ensure "Recur every: 1 days" is set.
    *   Click "Next".
4.  **Action:**
    *   Select "Start a program".
    *   Click "Next".
    *   **Program/script:** Enter the full path to your Python executable (e.g., `C:\Python39\python.exe` or `C:\Users\YourUser\AppData\Local\Programs\Python\Python39\python.exe`).
    *   **Add arguments (optional):** Enter the full path to your script: `run_daily_update.py`
    *   **Start in (optional):** Enter the absolute path to your project's root directory (e.g., `C:\path\to\your\project\`). This is important so the script can find other files like `scrape_reddit.py` and configurations correctly.
    *   It should look something like:
        *   Program/script: `C:\Path\To\Your\Python\python.exe`
        *   Add arguments: `run_daily_update.py`
        *   Start in: `C:\Path\To\Your\Project\RooCodeApp`
    *   Click "Next".
5.  **Finish:**
    *   Review the settings.
    *   Check the box "Open the Properties dialog for this task when I click Finish" if you want to adjust advanced settings (like running whether user is logged on or not, or running with highest privileges if necessary, though it shouldn't be for this script).
    *   Click "Finish".

6.  **Verify (Optional):** You can find the task in the Task Scheduler Library and run it manually once to ensure it works as expected. Check `daily_update.log` and `pushover.config.json` for results.

## 4. Checking Logs

*   The `run_daily_update.py` script logs its operations to `daily_update.log` in the project's root directory. Check this file for detailed information about each run.
*   If using `cron`, the `cron_output.log` (or whatever you named it) will contain output from the cron command itself, which can be useful if the script isn't even starting.

---

You should now have automated daily updates for your RooCode Data Query application with Pushover notifications!
