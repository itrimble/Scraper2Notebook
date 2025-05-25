import praw
import json
import sys # For sys.exit

# Configuration file path
CONFIG_FILE = "reddit.config.json"

# Load configuration
try:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    # Validate top-level keys
    if "reddit" not in config or "scrape_config" not in config:
        print(f"Error: '{CONFIG_FILE}' is missing required top-level keys ('reddit', 'scrape_config').")
        print(f"Please ensure '{CONFIG_FILE}' follows the structure of 'reddit.config.example.json'.")
        sys.exit(1)

    # Validate Reddit API credentials keys
    reddit_config = config["reddit"]
    required_reddit_keys = ["client_id", "client_secret", "user_agent"]
    if not all(key in reddit_config for key in required_reddit_keys):
        print(f"Error: 'reddit' section in '{CONFIG_FILE}' is missing one or more required keys: {required_reddit_keys}.")
        sys.exit(1)

    # Validate Scrape configuration keys
    scrape_config = config["scrape_config"]
    required_scrape_keys = ["subreddit", "post_limit", "output_file"]
    if not all(key in scrape_config for key in required_scrape_keys):
        print(f"Error: 'scrape_config' section in '{CONFIG_FILE}' is missing one or more required keys: {required_scrape_keys}.")
        sys.exit(1)

except FileNotFoundError:
    print(f"Error: Configuration file '{CONFIG_FILE}' not found.")
    print(f"Please create it by copying 'reddit.config.example.json' to '{CONFIG_FILE}'")
    print("and fill in your Reddit API credentials and desired scraping parameters.")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from '{CONFIG_FILE}'. Please check its syntax.")
    sys.exit(1)
except Exception as e: # Catch any other unexpected errors during config loading
    print(f"An unexpected error occurred while loading the configuration: {e}")
    sys.exit(1)


reddit = praw.Reddit(
    client_id=reddit_config["client_id"],
    client_secret=reddit_config["client_secret"],
    user_agent=reddit_config["user_agent"]
)
subreddit = reddit.subreddit(scrape_config["subreddit"])
with open(scrape_config["output_file"], "w") as f:
    for post in subreddit.top(limit=scrape_config["post_limit"]):
        f.write(f"{post.title}\n{post.selftext}\n")
        for comment in post.comments:
            if hasattr(comment, 'body'):
                f.write(f"{comment.body}\n")
