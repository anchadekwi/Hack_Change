import requests
import pandas as pd
from datetime import datetime
import time
import json


class VKontakteClient:
    def __init__(self, access_token: str, channel_uri: str, version: str = "5.131"):
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
        self.base_url = "https://api.vk.com/method/"

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
            if "vk.com/" in group_url:
                screen_name = group_url.split("vk.com/")[-1].split("?")[0]
            else:
                screen_name = group_url

            method = "groups.getById"
            params = {
                "group_ids": screen_name,
                "access_token": self.access_token,
                "v": self.version,
            }

            response = requests.get(f"{self.base_url}{method}", params=params)
            data = response.json()

            if "response" in data and len(data["response"]) > 0:
                group_id = data["response"][0]["id"]
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
                method = "wall.get"
                params = {
                    "owner_id": -self.group_id,
                    "count": count,
                    "offset": offset,
                    "extended": 1,
                    "access_token": self.access_token,
                    "v": self.version,
                }

                response = requests.get(f"{self.base_url}{method}", params=params)
                data = response.json()

                if "response" not in data or "items" not in data["response"]:
                    break

                posts_data = data["response"]["items"]

                # Парсим данные постов в нужный формат
                for post in posts_data:
                    # Пропускаем репосты и рекламные посты
                    if post.get("marked_as_ads") == 1 or post.get("copy_history"):
                        continue

                    post_info = {
                        "uri": f"https://vk.com/wall-{self.group_id}_{post['id']}",
                        "likes": post.get("likes", {}).get("count", 0),
                        "comment_count": post.get("comments", {}).get("count", 0),
                        "text": post.get("text", ""),
                        "publication_datetime": datetime.fromtimestamp(post["date"]),
                        "views": post.get("views", {}).get("count", 0),
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

    def extract_post_ids(self, post_uri: str) -> tuple:

        try:
            # Формат URI: https://vk.com/wall-{group_id}_{post_id}
            if "wall-" in post_uri:
                wall_part = post_uri.split("wall-")[-1]
                parts = wall_part.split("_")
                if len(parts) == 2:
                    group_id = abs(int(parts[0]))
                    post_id = int(parts[1])
                    return group_id, post_id
            raise ValueError("Некорректный формат URI")
        except Exception as e:
            return None, None

    def get_comments_from_post(self, post_uri: str, max_comments: int = 1000) -> list:

        # Извлекаем ID группы и поста
        group_id, post_id = self.extract_post_ids(post_uri)

        if not group_id or not post_id:
            return []

        comments_list = []
        count = 100  # Количество комментариев за запрос
        offset = 0

        while len(comments_list) < max_comments:
            try:
                # Получаем комментарии пачками
                method = "wall.getComments"
                params = {
                    "owner_id": -group_id,
                    "post_id": post_id,
                    "count": count,
                    "offset": offset,
                    "extended": 0,
                    "need_likes": 0,
                    "access_token": self.access_token,
                    "v": self.version,
                }

                response = requests.get(f"{self.base_url}{method}", params=params)
                data = response.json()

                # Проверяем ошибки
                if "error" in data:
                    error = data["error"]
                    error_code = error.get("error_code")
                    error_msg = error.get("error_msg")

                    if error_code == 15:
                        print(f"❌ Доступ запрещен: {error_msg}")
                    elif error_code == 100:
                        print(f"❌ Неверные параметры: {error_msg}")
                    else:
                        print(f"❌ Ошибка API: {error_msg}")
                    break

                # Проверяем наличие комментариев
                if "response" not in data or "items" not in data["response"]:
                    print("ℹ️ Комментарии не найдены")
                    break

                comments_data = data["response"]["items"]

                if not comments_data:
                    print("ℹ️ Больше нет комментариев")
                    break

                for comment in comments_data:

                    comment_time = datetime.fromtimestamp(comment["date"])
                    comment_text = comment.get("text", "").strip()

                    if comment_text:
                        comments_list.append(
                            {"text": comment_text, "publication_datetime": comment_time}
                        )

                if len(comments_data) < count:
                    break

                offset += count
                time.sleep(0.3)

            except Exception as e:
                break

        return comments_list


def main():
    # Создаем клиент с нужным интерфейсом
    client = VKontakteClient(
        "vk1.a.kIizzmzWeunee8CRKw3rwQkQ5KndhjWo1TAYZbbWPoRo2RUAS0gKW-y7jFKrvX3bCE7oOUdRHJxb95PrsW3jOVFs9PDvMJpkts3rqD0YRuJ6u73BoQgAwT-iydCDEyVkTTx_JI_GvRICI4cegamab_e-tRlhVAcDGOG_PCFz7CZVBCmygF4AtPlJIa9HSCdvUiVlFC4xHYc3V00qEhWf4A",
        "https://vk.com/rdrc_ru?from=groups",
    )
    # Получаем информацию о постах (соответствует интерфейсу)
    posts = client.get_posts_info()
    comments = client.get_comments_from_post("https://vk.com/wall-69473024_124934")
    print(posts)
    print(comments)


if __name__ == "__main__":
    main()
