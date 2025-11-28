import requests
import pandas as pd
from datetime import datetime
import time
import json

'''
class VKontakteClient(api, channel_uri):
    def get_posts_info(self, access_token, version='5.131') -> list ([{'uri': '', 'likes': 2, 'comment_count':666, 'text': '', 'publication_datetime': datetime}]
        self.access_token = access_token
        self.version = version
        self.base_url = 'https://api.vk.com/method/'
    def get_comments_for_post(self, post_uri: str) -> list ({'text': '', 'publication_datetime': datetime})'''

import requests
import pandas as pd
from datetime import datetime
import time


class VKontakteClient:
    def __init__(self, access_token: str, channel_uri: str, version: str = '5.131'):
        """
        Инициализация клиента VKontakte

        Args:
            access_token: Токен доступа VK API
            channel_uri: Ссылка на группу/канал VK
            version: Версия API VK
        """
        self.access_token = access_token
        self.channel_uri = channel_uri
        self.version = version
        self.base_url = 'https://api.vk.com/method/'

        # Получаем ID группы при инициализации
        self.group_id = self._get_group_id(channel_uri)
        if not self.group_id:
            raise ValueError(f"Не удалось получить ID группы для {channel_uri}")

    def _get_group_id(self, group_url: str) -> int:
        """
        Получает ID группы по ссылке
        """
        try:
            # Извлекаем короткое имя из ссылки
            if 'vk.com/' in group_url:
                screen_name = group_url.split('vk.com/')[-1].split('?')[0]
            else:
                screen_name = group_url

            method = 'groups.getById'
            params = {
                'group_ids': screen_name,
                'access_token': self.access_token,
                'v': self.version
            }

            response = requests.get(f"{self.base_url}{method}", params=params)
            data = response.json()

            if 'response' in data and len(data['response']) > 0:
                group_id = data['response'][0]['id']
                return abs(group_id)
            else:
                print(f"Ошибка получения ID группы: {data}")
                return None

        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def get_posts_info(self) -> list:
        """
        Получает информацию о постах

        Returns:
            list: Список словарей с информацией о постах в формате:
                  [{'uri': '', 'likes': 2, 'comment_count': 666, 'text': '', 'publication_datetime': datetime}]
        """
        all_posts = []
        count = 10000000  # Количество постов за один запрос
        offset = 0

        while True:
            try:
                # Получаем посты пачками
                method = 'wall.get'
                params = {
                    'owner_id': -self.group_id,
                    'count': count,
                    'offset': offset,
                    'extended': 1,
                    'access_token': self.access_token,
                    'v': self.version
                }

                response = requests.get(f"{self.base_url}{method}", params=params)
                data = response.json()

                if 'response' not in data or 'items' not in data['response']:
                    break

                posts_data = data['response']['items']

                # Парсим данные постов в нужный формат
                for post in posts_data:
                    # Пропускаем репосты и рекламные посты
                    if post.get('marked_as_ads') == 1 or post.get('copy_history'):
                        continue

                    post_info = {
                        'uri': f"https://vk.com/wall-{self.group_id}_{post['id']}",
                        'likes': post.get('likes', {}).get('count', 0),
                        'comment_count': post.get('comments', {}).get('count', 0),
                        'text': post.get('text', ''),
                        'publication_datetime': datetime.fromtimestamp(post['date'])
                    }

                    all_posts.append(post_info)

                print(f"Получено {len(posts_data)} постов. Всего: {len(all_posts)}")

                # Если получено меньше запрошенного количества, значит посты закончились
                if len(posts_data) < count:
                    break

                offset += count
                time.sleep(0.3)  # Задержка между запросами

            except Exception as e:
                print(f"Ошибка при получении постов: {e}")
                break

        return all_posts

    def get_comments_for_post(self, post_uri: str) -> list:
        """
        Получает комментарии для конкретного поста

        Args:
            post_uri: URI поста

        Returns:
            list: Список словарей с информацией о комментариях в формате:
                  [{'text': '', 'publication_datetime': datetime}]
        """
        # Извлекаем post_id из URI
        try:
            # Формат URI: https://vk.com/wall-{group_id}_{post_id}
            post_id = post_uri.split('_')[-1]
            if not post_id.isdigit():
                raise ValueError("Некорректный URI поста")
        except (IndexError, ValueError) as e:
            print(f"Ошибка извлечения post_id из URI: {e}")
            return []

        comments_info = []
        count = 1000000
        offset = 0

        while True:
            try:
                # Получаем комментарии пачками
                method = 'wall.getComments'
                params = {
                    'owner_id': -self.group_id,
                    'post_id': post_id,
                    'count': count,
                    'offset': offset,
                    'extended': 0,
                    'access_token': self.access_token,
                    'v': self.version
                }

                response = requests.get(f"{self.base_url}{method}", params=params)
                data = response.json()

                if 'response' not in data or 'items' not in data['response']:
                    break

                comments_data = data['response']['items']

                # Парсим комментарии в нужный формат
                for comment in comments_data:
                    comment_info = {
                        'text': comment.get('text', ''),
                        'publication_datetime': datetime.fromtimestamp(comment['date'])
                    }

                    comments_info.append(comment_info)

                print(f"Получено {len(comments_data)} комментариев. Всего: {len(comments_info)}")

                # Если получено меньше комментариев, значит больше нет
                if len(comments_data) < count:
                    break

                offset += count
                time.sleep(0.3)  # Задержка между запросами

            except Exception as e:
                print(f"Ошибка при получении комментариев: {e}")
                break

        return comments_info


def main():
    # Настройки
    ACCESS_TOKEN = '82672739826727398267273944815aab0e8826782672739eb4ec0e6a218285197132efa'
    GROUP_URL = input("Введите ссылку на группу VK: ").strip()

    try:
        # Создаем клиент с нужным интерфейсом
        client = VKontakteClient(ACCESS_TOKEN, GROUP_URL)

        #print(f"✅ Клиент инициализирован для группы: {GROUP_URL}")

        # Получаем информацию о постах (соответствует интерфейсу)
        print("🔄 Получаем информацию о постах...")
        posts = client.get_posts_info()

        print(f"\n✅ Собрано {len(posts)} постов")

        # Выводим статистику
        if posts:
            # Создаем DataFrame для удобства анализа
            df = pd.DataFrame(posts)

            print(f"\n📈 СТАТИСТИКА ГРУППЫ:")
            print(f"   Всего постов: {len(posts)}")
            print(f"   Средние показатели:")
            print(f"   ❤️  Лайки: {df['likes'].mean():.1f}")
            print(f"   💬 Комментарии: {df['comment_count'].mean():.1f}")

            # Пример получения комментариев для первого поста
            first_post_uri = posts[0]['uri']
            print(f"\n🔄 Получаем комментарии для первого поста...")
            comments = client.get_comments_for_post(first_post_uri)
            print(f"✅ Получено {len(comments)} комментариев")

        else:
            print("❌ Не удалось собрать посты")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()

