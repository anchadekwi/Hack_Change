import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from data_collector import YoutubeClient

# from llmclient import AdvancedEzmbedder


class MWSClient:
    def __init__(self, base_url: str, api_key: str, url_cm: str):
        """
        Initialize the MWSClient.

        :param base_url: Base URL for the API (e.g., "https://tables.mws.ru/fusion/v1/datasheets/dstEPg0bL9lD8jiDmt")
        :param api_key: Your API token for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.url_cm = url_cm.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def insert_rows(
        self, rows: List[Dict[str, Any]], view_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Insert rows into the datasheet.

        :param rows: List of dictionaries with the following keys:
                     - 'uri' (str)
                     - 'likes' (int)
                     - 'comment_count' (int)
                     - 'text' (str)
                     - 'publication_datetime' (datetime)
        :param view_id: Optional view ID to specify which view to use
        :return: API response as a dictionary
        """
        records = []
        for row in rows:
            # Convert datetime to milliseconds timestamp
            pub_timestamp = int(row["publication_datetime"].timestamp() * 1000)

            record = {
                "fields": {
                    "Ссылка": {"title": row["uri"], "text": row["uri"], "favicon": ""},
                    "Лайки": row["likes"],
                    "Комментарии": row["comment_count"],
                    "Пост": row["text"],
                    "Дата": pub_timestamp,
                    "Просмотры": row.get(
                        "views", None
                    ),  # Default value since it's not in input
                    "Название": row["text"][
                        :200
                    ],  # Default value since it's not in input
                    "Соц. сеть": row["source"],
                }
            }
            records.append(record)

        # Build URL
        url = f"{self.base_url}/records"
        if view_id:
            url += f"?viewId={view_id}&fieldKey=name"

        # Make API request
        response = requests.post(url, headers=self.headers, json={"records": records})

        response.raise_for_status()
        return response.json()

    def fetch_uris(self):
        response = requests.get(
            f"{self.base_url}/records?fieldKey=name&pageSize=1000", headers=self.headers
        )
        response.raise_for_status()

        return {
            i["fields"]["Ссылка"]["text"]: i["recordId"]
            for i in response.json()["data"]["records"]
            if "Ссылка" in i["fields"]
        }

    def delete_record(self, id):
        response = requests.delete(
            f"{self.base_url}/records?recordIds={id}",
            headers={k: v for k, v in self.headers.items() if k != "Content-Type"},
        )
        response.raise_for_status()

    def insert_updates(
        self, rows: List[Dict[str, Any]], view_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Insert rows into the datasheet.

        :param rows: List of dictionaries with the following keys:
                     - 'uri' (str)
                     - 'likes' (int)
                     - 'comment_count' (int)
                     - 'text' (str)
                     - 'publication_datetime' (datetime)
        :param view_id: Optional view ID to specify which view to use
        :return: API response as a dictionary
        """
        records = []
        for row in rows:
            # Convert datetime to milliseconds timestamp
            pub_timestamp = int(row["timestamp"].timestamp() * 1000)

            record = {
                "fields": {
                    "Ссылка": {"title": row["uri"], "text": row["uri"], "favicon": ""},
                    "Лайки": row["likes"],
                    "Комментарии": row["comment_count"],
                    "Дата": pub_timestamp,
                    "Просмотры": row.get(
                        "views", None
                    ),  # Default value since it's not in input
                }
            }
            records.append(record)

        # Build URL
        url = f"{self.base_url}/records"
        if view_id:
            url += f"?viewId={view_id}&fieldKey=name"

        # Make API request
        response = requests.post(url, headers=self.headers, json={"records": records})

        response.raise_for_status()
        return response.json()

    def insert_rows_for_comments(
        self, rows: List[Dict[str, Any]], view_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Insert rows into the datasheet.

        :param rows: List of dictionaries with the following keys:
                     - 'uri' (str)
                     - 'likes' (int)
                     - 'comment_count' (int)
                     - 'text' (str)
                     - 'publication_datetime' (datetime)
        :param view_id: Optional view ID to specify which view to use
        :return: API response as a dictionary
        """
        records = []
        for row in rows:
            # Convert datetime to milliseconds timestamp
            pub_timestamp = int(row["publication_datetime"].timestamp() * 1000)

            record = {
                "fields": {
                    "Ссылка на пост": {
                        "title": row["uri"],
                        "text": row["uri"],
                        "favicon": "",
                    },
                    "Текст": row["text"],
                    "Время публикации": pub_timestamp,
                    "Соц. сеть": row["source"],
                }
            }
            records.append(record)

        # Build URL
        url = f"{self.url_cm}/records"
        if view_id:
            url += f"?viewId={view_id}&fieldKey=name"

        # Make API request
        response = requests.post(url, headers=self.headers, json={"records": records})

        response.raise_for_status()
        return response.json()

    def fetch_post_uris(self):
        response = requests.get(
            f"{self.base_url}/records?fieldKey=name&pageSize=1000", headers=self.headers
        )
        response.raise_for_status()

        return [
            i["fields"]["Ссылка"]["text"]
            for i in response.json()["data"]["records"]
            if "Ссылка" in i["fields"]
        ]

    def fetch_comments_uris(self):
        result = []
        i = 1
        while True:
            response = requests.get(
                f"{self.url_cm}/records?fieldKey=name&pageSize=1000&pageNum={i}",
                headers=self.headers,
            )
            response.raise_for_status()
            st = [
                i["fields"]["Текст"]
                for i in response.json()["data"]["records"]
                if "Текст" in i["fields"]
            ]
            if not st:
                break
            i += 1
            result += st
        return list(set(result))


# if __name__ == "__main__":
#     print(
#         MWSClient(
#             "https://tables.mws.ru/fusion/v1/datasheets/dstEPg0bL9lD8jiDmt",
#             "uskPUFZhMwASVADEGwgI4XN",
#             "https://tables.mws.ru/fusion/v1/datasheets/dstCV00pr7W11osgz5"
#         ).fetch_comments_uris(
#         )
#     )
