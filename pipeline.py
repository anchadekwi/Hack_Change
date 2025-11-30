from mws_client import MWSClient
from tg_parser import TelegramClient
from vk_parser import VKontakteClient
from data_collector import YoutubeClient

mws_client = MWSClient(
    "https://tables.mws.ru/fusion/v1/datasheets/dstEPg0bL9lD8jiDmt",
    "uskPUFZhMwASVADEGwgI4XN",
    "https://tables.mws.ru/fusion/v1/datasheets/dstCV00pr7W11osgz5"
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
        "AIzaSyCdrOUYNbVUr3nmZARZ2dEOE8s8WzsVOSM",
        "https://www.youtube.com/@RollAllDay",
    )
    await telegram_parser.authenticate()

    existing_post_uris = mws_client.fetch_post_uris()

    posts_tg = await telegram_parser.get_posts_info()
    posts_vk = vk_parser.get_posts_info()
    posts_yt = yt_parser.get_videos_info()
    new_tg_rows = [
        i | {"source": "Телеграм"}
        for i in posts_tg
        if i["uri"] not in existing_post_uris
    ]
    print("TG new rows:", len(new_tg_rows))
    mws_client.insert_rows(new_tg_rows)
    new_vk_rows = [
        i | {"source": "ВК"} for i in posts_vk if i["uri"] not in existing_post_uris
    ]
    print("VK new rows:", len(new_vk_rows))
    mws_client.insert_rows(new_vk_rows)

    new_yt_rows = [
        i | {"source": "Ютуб"} for i in posts_yt if i["uri"] not in existing_post_uris
    ]
    print("YT new rows:", len(new_yt_rows))
    mws_client.insert_rows(new_yt_rows)

    existing_comments_uris = mws_client.fetch_comments_uris()

    comments_tg = await telegram_parser.get_comments_for_post("https://t.me/shucarz1337/771")
    comments_vk = vk_parser.get_comments_from_post("https://vk.com/wall-69473024_124934")
    comments_yt = yt_parser.get_comments_for_video("https://www.youtube.com/watch?v=UyaoBy3ETYI")

    new_tg_rows = [
        i | {"source": "Телеграм"}
        for i in comments_tg
        if i["text"] not in existing_comments_uris
    ]
    print("TG new comments:", len(new_tg_rows))
    mws_client.insert_rows_for_comments(new_tg_rows)
    new_vk_rows = [
        i | {"source": "ВК"} for i in comments_vk if i["text"] not in existing_comments_uris
    ]
    print("VK new comments:", len(new_vk_rows))
    mws_client.insert_rows_for_comments(new_vk_rows)

    new_yt_rows = [
        i | {"source": "Ютуб"} for i in comments_yt if i["text"] not in existing_comments_uris
    ]
    print("YT new comments:", len(new_yt_rows))
    mws_client.insert_rows_for_comments(new_yt_rows)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
