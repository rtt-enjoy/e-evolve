import tweepy

class Twitter:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.auth = tweepy.OAuthHandler(api_key, api_secret)
        self.api = tweepy.API(self.auth)

    def post_tweet(self, tweet):
        self.api.update_status(tweet)