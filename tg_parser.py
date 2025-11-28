import os
import asyncio
import pandas as pd
from datetime import datetime
import time
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import getpass
TELEGRAM_API_ID='38077916'
TELEGRAM_API_HASH='9c78424b3151f2f677a54e55bb2f2512'



class TelegramParser:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient('tg_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        self.is_authenticated = False

    async def authenticate(self):
        try:
            await self.client.start(
                phone=lambda: input(' Введите номер телефона (с кодом страны): '),
                password=lambda: getpass.getpass(' Введите пароль 2FA (если установлен): '),
                code_callback=lambda: input(' Введите код из Telegram: ')
            )
            self.is_authenticated = True
            print(" Аутентификация успешна!")
            return True
        except Exception as e:
            print(f" Ошибка аутентификации: {e}")
            return False

    async def get_channel_info(self, channel_url):
        try:

            if 't.me/' in channel_url:
                username = channel_url.split('t.me/')[-1].split('?')[0]
            elif channel_url.startswith('@'):
                username = channel_url[1:]
            else:
                username = channel_url


            channel = await self.client.get_entity(username)


            participants_count = getattr(channel, 'participants_count', None)

            channel_info = {
                'id': channel.id,
                'title': getattr(channel, 'title', 'Неизвестно'),
                'username': getattr(channel, 'username', 'Неизвестно'),
                'participants_count': participants_count,
                'description': getattr(channel, 'description', '')
            }

            return channel_info

        except Exception as e:
            print(f" Ошибка получения информации о канале: {e}")
            return None

    async def get_posts(self, channel_username, count=100, offset=0):
        try:

            channel = await self.client.get_entity(channel_username)
            posts = await self.client(GetHistoryRequest(
                peer=channel,
                limit=count,
                offset_date=None,
                offset_id=offset,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            return posts

        except Exception as e:
            print(f" Ошибка получения постов: {e}")
            return None

    def parse_posts_data(self, posts_data, channel_info):
        if not posts_data or not hasattr(posts_data, 'messages'):
            return []

        posts_info = []

        for message in posts_data.messages:
            if hasattr(message, 'message') and message.message:

                views = getattr(message, 'views', 0) or 0
                forwards = getattr(message, 'forwards', 0) or 0


                reactions = getattr(message, 'reactions', None)
                likes = 0
                if reactions and hasattr(reactions, 'results'):
                    for reaction in reactions.results:
                        likes += reaction.count


                post_date = message.date
                if post_date.tzinfo is not None:
                    post_date = post_date.replace(tzinfo=None)

                post_info = {
                    'post_id': message.id,
                    'date': post_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'text': message.message[:500],
                    'likes': likes,
                    'comments': 0,
                    'reposts': forwards,
                    'views': views,
                    'url': f"https://t.me/{channel_info['username']}/{message.id}",
                    'media_types': self._get_media_types(message)
                }

                posts_info.append(post_info)

        return posts_info

    def _get_media_types(self, message):

        media_types = []

        if hasattr(message, 'media'):
            if message.media:
                if hasattr(message.media, 'document'):
                    media_types.append('document')
                if hasattr(message.media, 'photo'):
                    media_types.append('photo')
                if hasattr(message.media, 'webpage'):
                    media_types.append('link')
                if hasattr(message.media, 'poll'):
                    media_types.append('poll')

        return ', '.join(media_types) if media_types else 'text'

    def _create_title(self, text):

        if not text:
            return "Без заголовка"

        first_line = text.split('\n')[0]
        if len(first_line) > 100:
            return first_line[:97] + "..."
        return first_line or "Информационный пост"


async def main():
    CHANNEL_URL = input("Введите ссылку на канал Telegram: ").strip()


    parser = TelegramParser(int(TELEGRAM_API_ID), TELEGRAM_API_HASH)

    print(" Аутентификация в Telegram...")
    auth_result = await parser.authenticate()

    if not auth_result:
        print("Не удалось пройти аутентификацию.")
        return

    print(" Получаем информацию о канале...")
    channel_info = await parser.get_channel_info(CHANNEL_URL)

    if not channel_info:
        print("Не удалось получить информацию о канале. Проверьте ссылку.")
        return

    print(f" Канал: {channel_info['title']} (@{channel_info['username']})")


    participants_count = channel_info['participants_count']
    if participants_count is not None and participants_count != 'Неизвестно':
        print(f" Подписчиков: {participants_count:,}")
    else:
        print(f" Подписчиков: Неизвестно")

    print(" Собираем посты...")


    all_posts = []
    count = 100
    offset = 0
    max_posts = 1000

    while len(all_posts) < max_posts:
        posts_data = await parser.get_posts(channel_info['username'], count=count, offset=offset)

        if not posts_data:
            break

        posts = parser.parse_posts_data(posts_data, channel_info)

        if not posts:
            break

        all_posts.extend(posts)
        print(f" Получено {len(posts)} постов. Всего: {len(all_posts)}")


        if len(posts) < count:
            break

        offset += count
        await asyncio.sleep(1)

    if not all_posts:
        print(" Не удалось собрать данные постов.")
        return


    df = pd.DataFrame(all_posts)


    df['engagement'] = (df['likes'] + df['comments'] + df['reposts']) / df['views'].replace(0, 1)
    df['engagement_rate'] = (df['engagement'] * 100).round(2)


    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"tg_posts_{channel_info['username']}_{timestamp}"


    df.to_csv(f"{filename}.csv", index=False, encoding='utf-8-sig')
    df.to_excel(f"{filename}.xlsx", index=False)
    df.to_json(f"{filename}.json", orient='records', indent=2, force_ascii=False)

    print(f"\n Собрано {len(df)} постов")
    print(f" Файлы сохранены как:")
    print(f"   - {filename}.csv")
    print(f"   - {filename}.xlsx")
    print(f"   - {filename}.json")


    print(f"\n📈 СТАТИСТИКА КАНАЛА '{channel_info['title']}':")
    print(f"   Всего постов: {len(df)}")
    print(f"   Средние показатели:")
    print(f"   👁️  Просмотры: {df['views'].mean():.0f}")
    print(f"   ❤️  Лайки: {df['likes'].mean():.1f}")
    print(f"   🔄 Репосты: {df['reposts'].mean():.1f}")
    print(f"   📊 Engagement Rate: {df['engagement_rate'].mean():.2f}%")


    print(f"\n🏆 ТОП-5 ПОСТОВ ПО ПРОСМОТРАМ:")
    top_views = df.nlargest(5, 'views')[['date', 'views', 'likes', 'reposts', 'url']]
    for idx, row in top_views.iterrows():
        print(f"   {row['date']} - 👁️ {row['views']} | ❤️ {row['likes']} | 🔄 {row['reposts']}")
        print(f"   🔗 {row['url']}")

    print(f"\n🔥 ТОП-5 ПОСТОВ ПО ЛАЙКАМ:")
    top_likes = df.nlargest(5, 'likes')[['date', 'likes', 'views', 'reposts', 'url']]
    for idx, row in top_likes.iterrows():
        print(f"   {row['date']} - ❤️ {row['likes']} | 👁️ {row['views']} | 🔄 {row['reposts']}")
        print(f"   🔗 {row['url']}")


def get_api_instructions():
    print("""
 ПОШАГОВАЯ ИНСТРУКЦИЯ ПОЛУЧЕНИЯ TELEGRAM API:

ШАГ 1: Получите API ключи
--------------------------
1. Перейдите: https://my.telegram.org/apps
2. Войдите через свой аккаунт Telegram
3. Нажмите "API Development Tools"
4. Заполните форму:
   - App title: MTS Parser (любое название)
   - Short name: mtsparser (латинскими буквами)
   - Platform: Web
   - Description: Parser for MTS hackathon
   - URL: https://example.com (можно любой)
5. Нажмите "Create application"
6. Скопируйте:
   - api_id (цифры)
   - api_hash (строка)

ШАГ 2: Настройка
-----------------
1. Сохраните api_id и api_hash
2. Используйте их при запуске скрипта

 ВАЖНО:
- API ключи привязаны к вашему аккаунту
- Не делитесь ими с другими
- Для работы нужен активный аккаунт Telegram
    """)


def quick_check():
    print(" Проверка настроек...")


    try:
        import telethon
        import pandas
        print(" Все библиотеки установлены")
    except ImportError as e:
        print(f" Не установлены библиотеки: {e}")
        print(" Установите: pip install telethon pandas openpyxl")
        return False

    return True


if __name__ == "__main__":

    print("TELEGRAM PARSER")



    if not quick_check():
        exit()


    show_instructions = input("Показать инструкцию по получению API ключей? (y/n): ").lower()
    if show_instructions == 'y':
        get_api_instructions()
        print("\n" + "=" * 60)


    asyncio.run(main())
