from mws_client import MWSClient
from tg_parser import TelegramClient
from vk_parser import VKontakteClient
from data_collector import YoutubeClient

mws_client = MWSClient(
    "https://tables.mws.ru/fusion/v1/datasheets/dstEPg0bL9lD8jiDmt",
    "uskPUFZhMwASVADEGwgI4XN",
)


async def main():
    telegram_parser = TelegramClient(
        "6276496", "5a2fd001f720903bd3d538e7b2c80cd3", "https://t.me/the_ai_architect"
    )
    vk_parser = VKontakteClient(
        "vk1.a.kIizzmzWeunee8CRKw3rwQkQ5KndhjWo1TAYZbbWPoRo2RUAS0gKW-y7jFKrvX3bCE7oOUdRHJxb95PrsW3jOVFs9PDvMJpkts3rqD0YRuJ6u73BoQgAwT-iydCDEyVkTTx_JI_GvRICI4cegamab_e-tRlhVAcDGOG_PCFz7CZVBCmygF4AtPlJIa9HSCdvUiVlFC4xHYc3V00qEhWf4A",
        "https://vk.com/rdrc_ru?from=groups",
    )
    yt_parser = YoutubeClient(
        "AIzaSyDIUvl2iJXBlDS0D1upZnb7azuzFfPq-hY",
        "https://www.youtube.com/@RollAllDay",
    )
    await telegram_parser.authenticate()
    posts_tg = await telegram_parser.get_posts_info()
    posts_vk = vk_parser.get_posts_info()
    posts_yt = yt_parser.get_videos_info()
    mws_client.insert_rows([i | {"source": "Телеграм"} for i in posts_tg])
    mws_client.insert_rows([i | {"source": "ВК"} for i in posts_vk])
    mws_client.insert_rows([i | {"source": "Ютуб"} for i in posts_yt])


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
