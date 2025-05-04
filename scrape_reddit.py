import praw
<<<<<<< HEAD

reddit = praw.Reddit(client_id="ELwPTiiusxvHHoeg5e4oYA", client_secret="jtyQ2SwdwdQjAhjqjK0JpdC6o5nMiw", user_agent="scraper")
=======
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID", 
    client_secret="YOUR_CLIENT_SECRET", 
    user_agent="YOUR_USER_AGENT"
)
>>>>>>> 4884a93c4df5a4baa10dac7648dce6b71f4a93c8
subreddit = reddit.subreddit("RooCode")
with open("reddit_data.txt", "w") as f:
    for post in subreddit.top(limit=100):
        f.write(f"{post.title}\n{post.selftext}\n")
        for comment in post.comments:
            if hasattr(comment, 'body'):
<<<<<<< HEAD
                f.write(f"{comment.body}\n")
=======
                f.write(f"{comment.body}\n")
>>>>>>> 4884a93c4df5a4baa10dac7648dce6b71f4a93c8
