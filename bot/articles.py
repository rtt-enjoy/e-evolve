import requests

class Article:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def post_to_devto(self):
        # dev.to posting logic
        pass

    def post_to_medium(self, integration_token):
        # Medium posting logic
        headers = {'Authorization': f'Bearer {integration_token}', 'Content-Type': 'application/json'}
        data = {'title': self.title, 'content': self.content}
        resp = requests.post('https://api.medium.com/v1/users/me/posts', headers=headers, json=data)
        if resp.status_code == 201:
            print('Article posted to Medium successfully')
        else:
            print('Error posting article to Medium')

    def post_to_both(self, devto_token, medium_token):
        self.post_to_devto()
        self.post_to_medium(medium_token)