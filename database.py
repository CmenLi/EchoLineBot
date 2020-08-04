import os
import json

from datetime import datetime

# <flags>
# user data flags
MEDIA_DOWNLOAD_FLAG = 1

# <files path>
media_download_log_file = 'static/media_download_log.json'


def read_user_data(flag: int, user: str):
    data = json.load(
        {
            1: open(media_download_log_file, mode='r', encoding='utf-8', errors='ignore')
        }[flag]
    )

    return data.get(user, {})


def log_media(user: str, media_type: str, name: str, url: str, duration: float, date: datetime):
    data: dict = read_user_data(1, user)
    media_id = 0
    if user in data:
        media_id = len(data["user"].get(media_type, []))
    else:
        data[user] = {"video": [], "audio": []}

    media_info = {
        "id": media_id,
        "name": name,
        "url": url,
        "duration": duration,
        "date": date.strftime('%Y/%m/%d')
    }

    media_list = data[user].get(media_type, [])
    media_list.add(media_info)
    data[user][media_type] = media_list

    print(data)

    with open(media_download_log_file) as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.close()
