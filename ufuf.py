import requests
import pandas as pd
from datetime import datetime
import time
import json


class VKParser:
    def __init__(self, access_token, version='5.131'):
        """
        Инициализация парсера VK

        Args:
            access_token: Токен доступа VK API
            version: Версия API
        """
        self.access_token = access_token
        self.version = version
        self.base_url = 'https://api.vk.com/method/'

    def get_group_id(self, group_url):
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
                group_name = data['response'][0]['name']
                return abs(group_id), group_name
            else:
                print(f"Ошибка получения ID группы: {data}")
                return None, None

        except Exception as e:
            print(f"Ошибка: {e}")
            return None, None

    def get_posts(self, group_id, count=100, offset=0):
        """
        Получает посты из группы
        """
        try:
            method = 'wall.get'
            params = {
                'owner_id': -group_id,  # Для групп используем отрицательный ID
                'count': count,
                'offset': offset,
                'extended': 1,  # Для получения информации о группе
                'fields': 'name,description',
                'access_token': self.access_token,
                'v': self.version
            }

            response = requests.get(f"{self.base_url}{method}", params=params)
            data = response.json()

            if 'response' in data:
                return data['response']
            else:
                print(f"Ошибка получения постов: {data}")
                return None

        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def parse_posts_data(self, posts_data):
        """
        Парсит данные постов
        """
        if not posts_data or 'items' not in posts_data:
            return []

        posts_info = []

        for post in posts_data['items']:
            # Пропускаем репосты и рекламные посты
            if post.get('marked_as_ads') == 1 or post.get('copy_history'):
                continue

            # Основные метрики
            views = post.get('views', {}).get('count', 0) if isinstance(post.get('views'), dict) else post.get('views',
                                                                                                               0)

            post_info = {
                'post_id': post['id'],
                'date': datetime.fromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M:%S'),
                'text': post.get('text', '')[:500],  # Ограничиваем длину текста
                'likes': post.get('likes', {}).get('count', 0),
                'comments': post.get('comments', {}).get('count', 0),
                'reposts': post.get('reposts', {}).get('count', 0),
                'views': views,
                'url': f"https://vk.com/wall-{abs(post['owner_id'])}_{post['id']}"
            }

            # Добавляем информацию о медиа
            if post.get('attachments'):
                media_types = []
                for attachment in post['attachments']:
                    media_type = attachment['type']
                    media_types.append(media_type)

                post_info['media_types'] = ', '.join(media_types)
            else:
                post_info['media_types'] = 'text'

            posts_info.append(post_info)

        return posts_info


def main():
    # Настройки
    ACCESS_TOKEN = '82672739826727398267273944815aab0e8826782672739eb4ec0e6a218285197132efa'  # Замените на ваш токен
    GROUP_URL = input("Введите ссылку на группу VK: ").strip()

    # Инициализация парсера
    parser = VKParser(ACCESS_TOKEN)

    print("Получаем ID группы...")
    group_id, group_name = parser.get_group_id(GROUP_URL)

    if not group_id:
        print("Не удалось получить ID группы. Проверьте ссылку и токен.")
        return

    print(f"Группа: {group_name} (ID: {group_id})")
    print("Собираем посты...")

    # Получаем посты
    all_posts = []
    count = 100  # Количество постов за один запрос
    offset = 0

    while True:
        posts_data = parser.get_posts(group_id, count=count, offset=offset)

        if not posts_data:
            break

        posts = parser.parse_posts_data(posts_data)

        if not posts:
            break

        all_posts.extend(posts)
        print(f"Получено {len(posts)} постов. Всего: {len(all_posts)}")

        # Если получено меньше запрошенного количества, значит посты закончились
        if len(posts) < count:
            break

        offset += count
        time.sleep(0.3)  # Задержка между запросами

    if not all_posts:
        print("Не удалось собрать данные постов.")
        return

    # Создаем DataFrame
    df = pd.DataFrame(all_posts)

    # Вычисляем дополнительные метрики
    df['engagement'] = (df['likes'] + df['comments'] + df['reposts']) / df['views'].replace(0, 1)
    df['engagement_rate'] = (df['engagement'] * 100).round(2)

    # Сохраняем в файлы
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"vk_posts_{group_name.replace(' ', '_')}_{timestamp}"

    # CSV
    df.to_csv(f"{filename}.csv", index=False, encoding='utf-8-sig')

    # Excel
    df.to_excel(f"{filename}.xlsx", index=False)

    # JSON
    df.to_json(f"{filename}.json", orient='records', indent=2, force_ascii=False)

    print(f"\n✅ Собрано {len(df)} постов")
    print(f"📊 Файлы сохранены как:")
    print(f"   - {filename}.csv")
    print(f"   - {filename}.xlsx")
    print(f"   - {filename}.json")

    # Выводим статистику
    print(f"\n📈 СТАТИСТИКА ГРУППЫ '{group_name}':")
    print(f"   Всего постов: {len(df)}")
    print(f"   Средние показатели:")
    print(f"   👁️  Просмотры: {df['views'].mean():.0f}")
    print(f"   ❤️  Лайки: {df['likes'].mean():.1f}")
    print(f"   💬 Комментарии: {df['comments'].mean():.1f}")
    print(f"   🔄 Репосты: {df['reposts'].mean():.1f}")
    print(f"   📊 Engagement Rate: {df['engagement_rate'].mean():.2f}%")

    # Топ постов
    print(f"\n🏆 ТОП-5 ПОСТОВ ПО ПРОСМОТРАМ:")
    top_views = df.nlargest(5, 'views')[['date', 'views', 'likes', 'comments', 'url']]
    for idx, row in top_views.iterrows():
        print(f"   {row['date']} - 👁️ {row['views']} | ❤️ {row['likes']} | 💬 {row['comments']}")
        print(f"   🔗 {row['url']}")

    print(f"\n🔥 ТОП-5 ПОСТОВ ПО ЛАЙКАМ:")
    top_likes = df.nlargest(5, 'likes')[['date', 'likes', 'views', 'comments', 'url']]
    for idx, row in top_likes.iterrows():
        print(f"   {row['date']} - ❤️ {row['likes']} | 👁️ {row['views']} | 💬 {row['comments']}")
        print(f"   🔗 {row['url']}")


if __name__ == "__main__":
    main()


'''
def generate_token_url(app_id):
    """
    Генерирует URL для получения токена
    """
    scopes = [
        'friends', 'photos', 'audio', 'video', 'stories', 'pages',
        'status', 'notes', 'messages', 'wall', 'ads', 'offline',
        'docs', 'groups', 'notifications', 'stats', 'email', 'market'
    ]

    scope_string = ','.join(scopes)

    url = f"""
🎯 URL для получения токена:

https://oauth.vk.com/authorize?client_id={app_id}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope={scope_string}&response_type=token&v=5.199&state=123456

📋 ИНСТРУКЦИЯ:
1. Скопируйте ссылку выше
2. Откройте в браузере
3. Нажмите "Разрешить"
4. Скопируйте token из адресной строки
   (параметр access_token после #access_token=)

Пример адресной строки после авторизации:
https://oauth.vk.com/blank.html#access_token=ваш_токен_здесь&expires_in=0&user_id=123456
"""
    return url


def get_token_manual_instructions(app_id):
    """
    Подробная инструкция по получению токена
    """
    print("""
📋 ПОШАГОВАЯ ИНСТРУКЦИЯ ПОЛУЧЕНИЯ ТОКЕНА:

ШАГ 1: Получите ID приложения
-----------------------------------
1. Перейдите: https://vk.com/apps?act=manage
2. Нажмите на ваше приложение
3. Скопируйте 'ID приложения'

ШАГ 2: Сгенерируйте ссылку для авторизации
-------------------------------------------
Используйте этот код для генерации ссылки:""")

    print(generate_token_url(app_id))

    print("""
ШАГ 3: Получите токен
---------------------
1. Откройте ссылку в браузере
2. Нажмите "Разрешить"
3. Из адресной строки скопируйте значение access_token

⚠️ ВАЖНО:
- Токен будет привязан к вашему аккаунту VK
- Для других пользователей нужно повторить процесс
- Токен имеет срок действия (если не указан scope=offline)
""")


# Пример использования
app_id = input("Введите ID вашего приложения: ")
get_token_manual_instructions(app_id)


if __name__ == "__main__":
    print("VK Token Validator")
    print("=" * 50)

    # Быстрая проверка
    if quick_token_check("5DnYUOGzts97h7Y8HWCb"):
        print("\n" + "=" * 50)
        # Если токен валиден, делаем полную проверку
        main()
    else:
        print("\n❌ Токен не прошел базовую проверку")'''