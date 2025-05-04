import praw
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID", 
    client_secret="YOUR_CLIENT_SECRET", 
    user_agent="YOUR_USER_AGENT"
)
subreddit = reddit.subreddit("RooCode")
with open("reddit_data.txt", "w") as f:
    for post in subreddit.top(limit=100):
        f.write(f"{post.title}\n{post.selftext}\n")
        for comment in post.comments:
            if hasattr(comment, 'body'):
                f.write(f"{comment.body}\n")
