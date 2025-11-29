import asyncio
from datetime import datetime
from telethon import TelegramClient as TelethonClient
from telethon.tl.functions.messages import GetHistoryRequest

TELEGRAM_API_ID = '38077916'
TELEGRAM_API_HASH = '9c78424b3151f2f677a54e55bb2f2512'


class TgClient:
    def __init__(self, api_id: str, api_hash: str, channel_uri: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.channel_uri = channel_uri
        self.client = TelethonClient('tg_session', api_id, api_hash)
        self.is_authenticated = False
        self.channel = None

    async def authenticate(self):
        try:
            await self.client.start()
            self.is_authenticated = True


            if 't.me/' in self.channel_uri:
                username = self.channel_uri.split('t.me/')[-1].split('?')[0].split('/')[0]
            elif self.channel_uri.startswith('@'):
                username = self.channel_uri[1:]
            else:
                username = self.channel_uri


            entity = await self.client.get_entity(username)


            from telethon.tl.types import Channel, ChatForbidden, ChannelForbidden

            if isinstance(entity, (ChatForbidden, ChannelForbidden)):
                print(f"Канал {username} недоступен (приватный или заблокирован)")
                return False

            if not hasattr(entity, 'username') or entity.username is None:
                print(f"У канала {username} нет публичного username — возможно, это приватный чат")
                return False


            if entity.username.lower() != username.lower():
                print(f"ОШИБКА: найден другой канал! Ожидался: {username}, найден: {entity.username}")
                return False



            self.channel = entity
            print(f"Успешно подключено к официальному каналу: {entity.title} (@{entity.username})")
            return True

        except Exception as e:
            print(f"Критическая ошибка аутентификации для {self.channel_uri}: {e}")
            return False

    async def get_posts_info(self) -> list([{'uri': '', 'likes': 2, 'comment_count':666, 'text': '', 'publication_datetime': datetime}]):

        if not self.is_authenticated:
            if not await self.authenticate():
                return []
        try:

            posts_data = await self.client(GetHistoryRequest(
                peer=self.channel,
                limit=1000000,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            posts_info = []
            for message in posts_data.messages:
                if hasattr(message, 'message') and message.message:

                    likes = 0
                    reactions = getattr(message, 'reactions', None)
                    if reactions and hasattr(reactions, 'results'):
                        for reaction in reactions.results:
                            likes += reaction.count


                    comment_count = 0
                    if hasattr(message, 'replies') and message.replies:
                        comment_count = message.replies.replies


                    post_date = message.date
                    if post_date.tzinfo is not None:
                        post_date = post_date.replace(tzinfo=None)

                    post_info = {
                        'uri': f"https://t.me/{self.channel.username}/{message.id}",
                        'likes': likes,
                        'comment_count': comment_count,
                        'text': message.message,
                        'publication_datetime': post_date
                    }

                    posts_info.append(post_info)

            return posts_info

        except Exception as e:
            print(f"Ошибка получения постов: {e}")
            return []

    async def get_comments_for_post(self, post_uri: str) -> list[dict]:

        try:
            if not post_uri.startswith("https://t.me/"):
                return []

            parts = post_uri.replace("https://t.me/", "").split("/")
            if len(parts) < 2:
                return []

            channel_username = parts[0]
            message_id = int(parts[1].split("?")[0])


            if not self.channel or self.channel.username != channel_username:
                self.channel = await self.client.get_entity(channel_username)


            message = await self.client.get_messages(self.channel, ids=message_id)
            if not message:
                return []


            if not hasattr(message, 'replies') or not message.replies or message.replies.replies == 0:
                return []


            comments = []
            async for comment in self.client.iter_messages(
                    entity=self.channel,
                    reply_to=message_id,
                    limit=500  
            ):
                if not comment.message:
                    continue

                comment_date = comment.date
                if comment_date.tzinfo:
                    comment_date = comment_date.replace(tzinfo=None)

                comments.append({
                    'text': comment.message.strip(),
                    'publication_datetime': comment_date
                })

            return comments

        except Exception as e:
            print(f"Ошибка при получении комментариев для {post_uri}: {e}")
            return []


async def main():
    link = input('Введите ссылку: ')
    client = TgClient(TELEGRAM_API_ID, TELEGRAM_API_HASH, link)
    posts = await client.get_posts_info()
    print(f"Получено постов: {len(posts)}")
    print(posts)
    if posts:
        comments = await client.get_comments_for_post(posts[0]['uri'])
        print(comments)


if __name__ == "__main__":
    asyncio.run(main())

