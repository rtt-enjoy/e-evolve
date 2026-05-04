import tweepy

def post_to_twitter(api_key, api_secret, article):
    auth = tweepy.OAuthHandler(api_key, api_secret)
    api = tweepy.API(auth)
    tweet = article['title'] + ' ' + article['link']
    api.update_status(tweet)