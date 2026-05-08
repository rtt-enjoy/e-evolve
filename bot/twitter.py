import os
import tweepy

twitter_api_key = os.environ.get('TWITTER_API_KEY')
twitter_api_secret = os.environ.get('TWITTER_API_SECRET')
twitter_access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
twitter_access_secret = os.environ.get('TWITTER_ACCESS_SECRET')

def post_to_twitter(text):
    auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
    auth.set_access_token(twitter_access_token, twitter_access_secret)
    api = tweepy.API(auth)
    api.update_status(status=text)