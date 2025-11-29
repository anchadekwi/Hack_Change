import requests
from datetime import datetime
from typing import List, Dict, Any, Optional


class MWSClient:
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the MWSClient.

        :param base_url: Base URL for the API (e.g., "https://tables.mws.ru/fusion/v1/datasheets/dstEPg0bL9lD8jiDmt")
        :param api_key: Your API token for authentication
        """
        self.base_url = base_url.rstrip("/")
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
                    "Ссылка": {"title": "prikol", "text": row["uri"], "favicon": ""},
                    "Лайки": row["likes"],
                    "Комментарии": row["comment_count"],
                    "Пост": row["text"],
                    "Дата": pub_timestamp,
                    "Просмотры": row.get(
                        "views", ""
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


if __name__ == "__main__":
    print(
        MWSClient(
            "https://tables.mws.ru/fusion/v1/datasheets/dstEPg0bL9lD8jiDmt",
            "uskPUFZhMwASVADEGwgI4XN",
        ).insert_rows(
            [
                {
                    "uri": "xy",
                    "likes": 1,
                    "comment_count": 500,
                    "text": "qweqweqwe",
                    "publication_datetime": datetime(2025, 11, 11),
                }
            ]
        )
    )
