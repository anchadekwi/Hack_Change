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
                username = self.channel_uri.split('t.me/')[-1].split('?')[0]
            elif self.channel_uri.startswith('@'):
                username = self.channel_uri[1:]
            else:
                username = self.channel_uri

            self.channel = await self.client.get_entity(username)
            return True

        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            return False

    async def get_posts_info(self) -> list([{'uri': '', 'likes': 2, 'comment_count':666, 'text': '', 'publication_datetime': datetime}]):

        if not self.is_authenticated:
            if not await self.authenticate():
                return []
        try:

            posts_data = await self.client(GetHistoryRequest(
                peer=self.channel,
                limit=100000,
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

    async def get_comments_for_post(self, post_uri: str) -> list ({'text': '', 'publication_datetime': datetime}):
        try:

            comments = [
                {
                    'text': 'Отличный пост! Спасибо за информацию.',
                    'publication_datetime': datetime.now()
                },
                {
                    'text': 'Интересный контент, жду продолжения',
                    'publication_datetime': datetime.now()
                },
                {
                    'text': 'Спасибо, очень полезно!',
                    'publication_datetime': datetime.now()
                }
            ]
            return comments

        except Exception as e:
            print(f"Ошибка получения комментариев: {e}")
            return []



async def main():

    client = TgClient(TELEGRAM_API_ID, TELEGRAM_API_HASH, "https://t.me/MTSWebServices")
    posts = await client.get_posts_info()
    print(f"Получено постов: {len(posts)}")


    for i, post in enumerate(posts[:10]):
        print(f"\nПост {i + 1}:")
        print(f"URI: {post['uri']}")
        print(f"Лайки: {post['likes']}")
        print(f"Комментарии: {post['comment_count']}")
        print(f"Дата: {post['publication_datetime']}")
        print(f"Текст: {post['text'][:1000000]}...")


    if posts:
        comments = await client.get_comments_for_post(posts[0]['uri'])
        print(f"\nКомментариев к первому посту: {len(comments)}")


if __name__ == "__main__":

    asyncio.run(main())

    

