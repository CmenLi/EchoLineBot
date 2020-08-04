import os
import json

from datetime import datetime

# <flags>
# user data flags
MEDIA_DOWNLOAD_FLAG = 1

# <files path>
media_download_log_file = 'static/media_download_log.json'


def read_data(flag: int):
    data = json.load(
        {
            1: open(media_download_log_file, mode='r', encoding='utf-8', errors='ignore')
        }[flag]
    )

    return data


def read_user_data(flag: int, user: str):
    data = json.load(
        {
            1: open(media_download_log_file, mode='r', encoding='utf-8', errors='ignore')
        }[flag]
    )

    return data.get(user, {})


def log_media(user: str, media_type: str, name: str, url: str, duration: float, date: datetime):
    data: dict = read_data(1)
    user_data = data.get(user, {})
    media_id = len(user_data.get(media_type, []))

    media_info = {
        "id": media_id,
        "name": name,
        "url": url,
        "duration": duration,
        "date": date.strftime('%Y/%m/%d')
    }

    media_list = user_data.get(media_type, [])
    media_list.add(media_info)
    user_data[media_type] = media_list
    data[user] = user_data

    print(data)

    with open(media_download_log_file) as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.close()
