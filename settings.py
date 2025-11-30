import requests


class Settings:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def fetch_post_uris(self):
        response = requests.get(
            f"{self.base_url}/records?fieldKey=name&pageSize=1000", headers=self.headers
        )
        response.raise_for_status()
        return [response.json()['data']['records'][0]['fields']['URL ютуб']['text'],
                response.json()['data']['records'][0]['fields']['URL телеграм']['text'],
                response.json()['data']['records'][0]['fields']['URL ВК']['text']]
