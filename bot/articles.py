import requests

def post_to_medium(token, article):
    url = 'https://api.medium.com/v1/users/me/posts'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = {'title': article['title'], 'content': article['content']}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print('Article posted to Medium successfully')
    else:
        print('Error posting article to Medium')