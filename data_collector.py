# working_youtube_fixed.py
import requests
import json
import os
from typing import Dict, List, Optional


class YouTubeAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('AIzaSyD4OQJynLzAgh3u7ZHsiwQzzr7msKFh9ZI')
        if not self.api_key:
            raise ValueError("YouTube API key is required")

        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.session = requests.Session()

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Выполнение запроса к YouTube API"""
        url = f"{self.base_url}/{endpoint}"
        params['key'] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f"API request failed: {str(e)}"}

    def _extract_video_id(self, url: str) -> str:
        """Извлечение ID видео из URL"""
        import re
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&?\s]+)',
            r'youtube\.com/embed/([^&?\s]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return url  # Если передан чистый ID

    def get_video_stats(self, video_identifier: str) -> Dict:
        """Получение статистики видео"""
        video_id = self._extract_video_id(video_identifier)

        params = {
            'part': 'statistics,snippet,contentDetails',
            'id': video_id
        }

        data = self._make_request('videos', params)

        if 'error' in data:
            return data

        if not data.get('items'):
            return {'error': 'Video not found'}

        video_data = data['items'][0]
        statistics = video_data['statistics']
        snippet = video_data['snippet']
        content_details = video_data.get('contentDetails', {})

        # Преобразуем числа, обрабатывая возможные ошибки
        try:
            views = int(statistics.get('viewCount', 0))
        except (ValueError, TypeError):
            views = 0

        try:
            likes = int(statistics.get('likeCount', 0))
        except (ValueError, TypeError):
            likes = 0

        try:
            comments = int(statistics.get('commentCount', 0))
        except (ValueError, TypeError):
            comments = 0

        result = {
            'video_id': video_id,
            'title': snippet.get('title', 'Unknown'),
            'description': snippet.get('description', '')[:200],
            'channel_title': snippet.get('channelTitle', 'Unknown'),
            'published_at': snippet.get('publishedAt', 'Unknown'),
            'duration': content_details.get('duration', 'Unknown'),
            'views': views,
            'likes': likes,
            'comments': comments,
        }

        print(f"✅ Данные успешно получены: {result['title'][:50]}...")
        return result

    def get_video_comments(self, video_identifier: str, max_comments: int = 50) -> Dict:
        """Получение комментариев к видео"""
        video_id = self._extract_video_id(video_identifier)

        print(f"💬 Загружаем комментарии для видео {video_id}...")

        comments = []
        next_page_token = None

        try:
            while len(comments) < max_comments:
                params = {
                    'part': 'snippet',
                    'videoId': video_id,
                    'maxResults': min(100, max_comments - len(comments)),
                    'textFormat': 'plainText',
                    'order': 'relevance'
                }

                if next_page_token:
                    params['pageToken'] = next_page_token

                data = self._make_request('commentThreads', params)

                if 'error' in data:
                    error_msg = data['error']
                    if 'comments disabled' in error_msg.lower():
                        return {'error': 'Comments are disabled for this video', 'comments': [], 'total_count': 0}
                    return data

                if not data.get('items'):
                    break

                for item in data['items']:
                    comment_data = item['snippet']['topLevelComment']['snippet']

                    comment = {
                        'id': item['id'],
                        'author': comment_data.get('authorDisplayName', 'Unknown'),
                        'text': comment_data.get('textDisplay', ''),
                        'likes': int(comment_data.get('likeCount', 0)),
                        'published_at': comment_data.get('publishedAt', ''),
                    }
                    comments.append(comment)

                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break

                # Небольшая задержка между запросами
                import time
                time.sleep(0.1)

            # Анализ комментариев
            analysis = self._analyze_comments(comments)

            return {
                'comments': comments[:max_comments],
                'total_count': len(comments),
                'analysis': analysis,
                'success': True
            }

        except Exception as e:
            return {'error': f"Unexpected error: {str(e)}", 'comments': [], 'total_count': 0}

    def _analyze_comments(self, comments: List[Dict]) -> Dict:
        """Анализ комментариев"""
        if not comments:
            return {
                'total_comments': 0,
                'average_length': 0,
                'total_likes': 0,
                'most_liked_comment': None,
            }

        total_chars = sum(len(comment.get('text', '')) for comment in comments)
        total_likes = sum(comment.get('likes', 0) for comment in comments)
        avg_length = total_chars / len(comments)

        most_liked = max(comments, key=lambda x: x.get('likes', 0)) if comments else None

        return {
            'total_comments': len(comments),
            'average_length': round(avg_length, 2),
            'total_likes': total_likes,
            'most_liked_comment': {
                'author': most_liked.get('author', '') if most_liked else None,
                'text': (most_liked.get('text', '')[:100] + '...') if most_liked else None,
                'likes': most_liked.get('likes', 0) if most_liked else 0,
            } if most_liked else None
        }


def main():

    api_key = "AIzaSyD4OQJynLzAgh3u7ZHsiwQzzr7msKFh9ZI"

    try:
        youtube = YouTubeAPI(api_key)
        print("✅ YouTube API инициализирован!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # Тестовые запросы
    test_videos = [
        "https://www.youtube.com/watch?v=UyaoBy3ETYI",
    ]

    for video_url in test_videos:
        print(f"\n{'=' * 60}")
        print(f"🎬 Анализ: {video_url}")
        print('=' * 60)

        # Получаем статистику
        print("📊 Получаем статистику...")
        stats = youtube.get_video_stats(video_url)

        if 'error' in stats:
            print(f"❌ Ошибка: {stats['error']}")
            continue

        # Выводим статистику
        print("✅ Статистика получена!")
        print(f"\n📹 Заголовок: {stats['title']}")
        print(f"👤 Канал: {stats['channel_title']}")
        print(f"👁️  Просмотры: {stats['views']:,}")
        print(f"👍  Лайки: {stats['likes']:,}")
        print(f"💬 Комментарии: {stats['comments']:,}")

        # Считаем engagement rate
        if stats['views'] > 0:
            engagement = (stats['likes'] / stats['views']) * 100
            print(f"📈 Engagement Rate: {engagement:.4f}%")

        # Получаем комментарии если они есть
        if stats['comments'] > 0:
            print(f"\n💬 Получаем комментарии...")
            comments_data = youtube.get_video_comments(video_url, max_comments=100)

            if 'error' in comments_data:
                print(f"ℹ️  {comments_data['error']}")
            else:
                analysis = comments_data['analysis']
                print(f"✅ Собрано комментариев: {analysis['total_comments']}")

                if comments_data['comments']:
                    print(f"\n📝 Примеры комментариев:")
                    for i, comment in enumerate(comments_data['comments'][:3], 1):
                        print(f"   {i}. 👤 {comment['author']} ({comment['likes']} ❤️)")
                        print(f"      💬 {comment['text'][:80]}...")
        else:
            print(f"\n💬 У видео нет комментариев")

        print(f"\n✅ Анализ завершен для {stats['video_id']}")


if __name__ == "__main__":
    # Запускаем основную демонстрацию
    main()