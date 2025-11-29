import requests
from typing import Dict, List
from datetime import datetime
import re


class YoutubeClient:
    def __init__(self, api_key: str, channel_uri: str):
        self.api_key = api_key
        self.channel_uri = channel_uri
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.session = requests.Session()

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Выполнение запроса к YouTube API"""
        url = f"{self.base_url}/{endpoint}"
        params["key"] = self.api_key

        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def _get_channel_id_from_username(self, username: str) -> str:
        """Получение channel_id из username (@username)"""
        params = {"part": "id", "forUsername": username}

        data = self._make_request("channels", params)

        if "error" in data or not data.get("items"):
            return ""

        return data["items"][0]["id"]

    def _extract_channel_id(self, channel_uri: str) -> str:
        """Извлечение ID канала из URI"""
        if channel_uri.startswith("UC") and len(channel_uri) == 24:
            return channel_uri

        if "@" in channel_uri:
            username_match = re.search(r"@([a-zA-Z0-9_-]+)", channel_uri)
            if username_match:
                username = username_match.group(1)
                return self._get_channel_id_from_username(username)

        patterns = [
            r"channel/([a-zA-Z0-9_-]{24})",
            r"youtube\.com/channel/([a-zA-Z0-9_-]{24})",
        ]

        for pattern in patterns:
            match = re.search(pattern, channel_uri)
            if match:
                return match.group(1)

        return ""

    def _extract_channel_id(self, channel_uri: str) -> str:
        """Извлечение ID канала из URI с поддержкой @username"""

        # Если это уже channel_id (начинается с UC)
        if channel_uri.startswith("UC") and len(channel_uri) == 24:
            return channel_uri

        # Если это @username
        if "@" in channel_uri:
            username_match = re.search(r"@([a-zA-Z0-9_-]+)", channel_uri)
            if username_match:
                username = username_match.group(1)
                return self._get_channel_id_from_username(username)

        # Пробуем извлечь из URL
        patterns = [
            r"channel/([a-zA-Z0-9_-]{24})",
            r"youtube\.com/channel/([a-zA-Z0-9_-]{24})",
        ]

        for pattern in patterns:
            match = re.search(pattern, channel_uri)
            if match:
                channel_id = match.group(1)
                return channel_id

        print("❌ Не удалось извлечь channel_id")
        return ""

    def _parse_datetime(self, datetime_str: str) -> datetime:
        """Парсинг datetime из строки YouTube"""
        try:
            return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        except:
            return datetime.now()

    def get_videos_info(self) -> List[Dict]:
        """Получает канал и возвращает структуру по всем видео канала"""
        channel_id = self._extract_channel_id(self.channel_uri)

        if not channel_id:
            return []

        videos = []
        next_page_token = None

        channel_params = {"part": "snippet", "id": channel_id}

        channel_data = self._make_request("channels", channel_params)

        if "error" in channel_data or not channel_data.get("items"):
            raise Exception(channel_data)

        while True:
            params = {
                "part": "id,snippet",
                "channelId": channel_id,
                "maxResults": 50,
                "order": "date",
                "type": "video",
            }

            if next_page_token:
                params["pageToken"] = next_page_token

            search_data = self._make_request("search", params)

            if "error" in search_data or not search_data.get("items"):
                break

            video_ids = []
            for item in search_data["items"]:
                if "videoId" in item["id"]:
                    video_ids.append(item["id"]["videoId"])

            if not video_ids:
                break

            stats_params = {"part": "statistics,snippet", "id": ",".join(video_ids)}

            videos_data = self._make_request("videos", stats_params)

            if "error" in videos_data or not videos_data.get("items"):
                break

            for video_data in videos_data["items"]:
                statistics = video_data.get("statistics", {})
                snippet = video_data.get("snippet", {})

                try:
                    likes = int(statistics.get("likeCount", 0))
                except (ValueError, TypeError):
                    likes = 0

                try:
                    comment_count = int(statistics.get("commentCount", 0))
                except (ValueError, TypeError):
                    comment_count = 0

                video_info = {
                    "uri": f"https://www.youtube.com/watch?v={video_data['id']}",
                    "views": (
                        int(statistics["viewCount"])
                        if "viewCount" in statistics
                        else None
                    ),
                    "likes": likes,
                    "comment_count": comment_count,
                    "text": snippet.get("title", ""),
                    "publication_datetime": self._parse_datetime(
                        snippet.get("publishedAt", "")
                    ),
                    "description": int(statistics["viewCount"]),
                }
                videos.append(video_info)

            next_page_token = search_data.get("nextPageToken")
            if not next_page_token:
                break

            import time

            time.sleep(0.1)

        return videos

    def get_comments_for_video(self, video_uri: str) -> List[Dict]:
        """Получение комментариев для видео"""
        video_id = self._extract_video_id(video_uri)

        if not video_id or len(video_id) != 11:
            return []

        comments = []
        next_page_token = None

        while True:
            params = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": 100,
                "textFormat": "plainText",
            }

            if next_page_token:
                params["pageToken"] = next_page_token

            data = self._make_request("commentThreads", params)

            if "error" in data:
                return comments

            if not data.get("items"):
                break

            for item in data["items"]:
                comment_data = item["snippet"]["topLevelComment"]["snippet"]

                comment = {
                    "text": comment_data.get("textDisplay", ""),
                    "publication_datetime": self._parse_datetime(
                        comment_data.get("publishedAt", "")
                    ),
                }
                comments.append(comment)

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

            import time

            time.sleep(0.1)

        return comments


# youtube = YoutubeClient("AIzaSyBB1nT_RE1FVHTvzcdF1e2FxBta7i7GFh8", "https://www.youtube.com/@pognalishow")

# # Получение всех видео канала
# videos = youtube.get_videos_info()
# print(videos)
# Получение комментариев для конкретного видео
# comments = youtube.get_comments_for_video("https://www.youtube.com/watch?v=UyaoBy3ETYI")
