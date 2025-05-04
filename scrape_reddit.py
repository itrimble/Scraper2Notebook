import praw

reddit = praw.Reddit(client_id="ELwPTiiusxvHHoeg5e4oYA", client_secret="jtyQ2SwdwdQjAhjqjK0JpdC6o5nMiw", user_agent="scraper")
subreddit = reddit.subreddit("RooCode")
with open("reddit_data.txt", "w") as f:
    for post in subreddit.top(limit=100):
        f.write(f"{post.title}\n{post.selftext}\n")
        for comment in post.comments:
            if hasattr(comment, 'body'):
                f.write(f"{comment.body}\n")