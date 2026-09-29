import os
import requests

def get_github_session():
    token = os.getenv("GITHUB_TOKEN")
    session = requests.Session()
    if token:
        session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "e-evolve-code-techs"
        })
    return session

def github_get(url, **kwargs):
    sess = get_github_session()
    response = sess.get(url, **kwargs)
    response.raise_for_status()
    return response.json()