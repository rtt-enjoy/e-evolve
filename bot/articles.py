# Article publishing module
class Article:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def post_to_devto(self, devto_token):
        # dev.to posting logic
        headers = {'api-key': devto_token, 'Content-Type': 'application/json'}
        payload = {
            'article': {
                'title': self.title[:80],
                'body_markdown': self.content,
                'description': self.title[:150],
                'published': True,
                'tags': ['python', 'automation']
            }
        }
        try:
            import requests
            resp = requests.post('https://dev.to/api/articles', headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get('url', '')
        except Exception as exc:
            print(f'Error posting to dev.to: {exc}')
            return ''

    def post_to_medium(self, integration_token):
        # Medium posting logic
        headers = {'Authorization': f'Bearer {integration_token}', 'Content-Type': 'application/json'}
        data = {'title': self.title, 'content': self.content, 'publishStatus': 'public'}
        try:
            import requests
            resp = requests.post('https://api.medium.com/v1/users/me/posts', headers=headers, json=data, timeout=30)
            if resp.status_code == 201:
                return resp.json().get('url', '')
            else:
                print(f'Error posting to Medium: {resp.status_code} - {resp.text}')
                return ''
        except Exception as exc:
            print(f'Error posting to Medium: {exc}')
            return ''

    def post_to_both(self, devto_token, medium_token):
        devto_url = self.post_to_devto(devto_token)
        medium_url = self.post_to_medium(medium_token)
        return devto_url, medium_url