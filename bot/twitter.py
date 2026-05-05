import requests

class Twitter:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def post_tweet(self, tweet):
        # Twitter posting logic
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
        data = {'text': tweet}
        response = requests.post('https://api.twitter.com/2/tweets', headers=headers, json=data)
        return response.json()