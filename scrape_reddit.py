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


# --- Main scraping logic ---
def main_scraping_logic():
    print("Initializing PRAW client...")
    reddit = praw.Reddit(
        client_id=reddit_config["client_id"],
        client_secret=reddit_config["client_secret"],
        user_agent=reddit_config["user_agent"]
    )
    print(f"Fetching posts from subreddit: {scrape_config['subreddit']} with limit: {scrape_config['post_limit']}")
    subreddit = reddit.subreddit(scrape_config["subreddit"])
    
    output_file = scrape_config["output_file"]
    print(f"Attempting to write scraped data to: {output_file}")
    
    posts_written = 0
    comments_written = 0

    with open(output_file, "w", encoding='utf-8') as f: # Added encoding
        for post in subreddit.top(limit=scrape_config["post_limit"]):
            f.write(f"Title: {post.title}\n") # Added "Title: " prefix for clarity
            # Ensure selftext is not None and handle potential newlines within selftext
            selftext = post.selftext.replace('\n', ' ') if post.selftext else ""
            f.write(f"Selftext: {selftext}\n") # Added "Selftext: " prefix
            posts_written += 1
            
            # Fetch comments for the post
            # Using .comments.list() to get all comments, then iterating
            # This avoids issues with MoreComments objects if not replacing them.
            # For simplicity, let's stick to the existing direct iteration if it works for top-level.
            # If MoreComments is an issue, one might need post.comments.replace_more(limit=0)
            # then iterate post.comments.list()
            post.comments.replace_more(limit=0) # Ensure all comments are loaded
            for comment in post.comments.list(): # Iterate through the flattened list of comments
                if hasattr(comment, 'body'):
                    # Ensure comment body is not None and handle potential newlines
                    comment_body = comment.body.replace('\n', ' ') if comment.body else ""
                    if comment_body: # Only write if there's a body
                        f.write(f"Comment: {comment_body}\n") # Added "Comment: " prefix
                        comments_written += 1
            f.write("---\n") # Separator between posts
    
    print(f"Scraping complete. {posts_written} posts and {comments_written} comments written to {output_file}.")

if __name__ == "__main__":
    try:
        # Configuration loading is already handled above and exits on failure.
        # If execution reaches here, config loading was successful.
        main_scraping_logic()
        print("scrape_reddit.py executed successfully.")
        sys.exit(0)
    except praw.exceptions.PRAWException as e:
        print(f"A PRAW (Reddit API) related error occurred: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"An I/O error occurred (e.g., writing to file {scrape_config.get('output_file', 'output.txt')}): {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
=======

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

