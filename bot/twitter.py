import requests

def post_to_twitter(api_key, api_secret, tweet):
    url = 'https://api.twitter.com/2/tweets'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {'text': tweet}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print('Tweet posted successfully')
    else:
        print('Error posting tweet')