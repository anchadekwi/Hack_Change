from mws_client import MWSClient
from tg_parser import TgClient

mws_client = MWSClient(
    "https://tables.mws.ru/fusion/v1/datasheets/dstEPg0bL9lD8jiDmt",
    "uskPUFZhMwASVADEGwgI4XN",
)


async def main():
    telegram_parser = TgClient(
        "6276496", "5a2fd001f720903bd3d538e7b2c80cd3", "https://t.me/the_ai_architect"
    )
    await telegram_parser.authenticate()
    posts_tg = await telegram_parser.get_posts_info()
    mws_client.insert_rows([i | {"source": "Телеграм"} for i in posts_tg])


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
