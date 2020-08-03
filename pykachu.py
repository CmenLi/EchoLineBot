from __future__ import unicode_literals
import os

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import random

import configparser
import json

from yt_downloader import Downloader

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# variables
# const:
DOMAIN = 'https://pykachu-linebot.herokuapp.com/'

ADMIN_ID = 'U940d15d3a94c5e90dde5e52dd373d0be'

HACKMD_URL = 'https://hackmd.io/@KoiSharp/H1l7A7kRI'
GOOGLE_DRIVE_URL = 'https://drive.google.com/drive/folders/13YSMSTgxpUFwUzXafZbvlbZk89yJPvNF?usp=sharing'
WEBSITE_URL = 'https://pykachu-website.herokuapp.com/resources.jsp'

help_board = '========小幫手========\n' \
             ';;bot                                       - 功能介面\n' \
             ';;md                                        - 查看HackMD筆記\n' \
             ';;drive                                     - 查看共享資料\n' \
             ';;web                                       - 查看網站(比賽資料)\n' \
             ';;dl [audio(-a)|video(-v)] [youtube url]    - 從youtube下載影片或音樂\n' \
             ';;bye                                       - 掰掰'

leave_msg_list = ['掰掰♪ 有需要再找我呦~',
                  '怎麼趕我走! QAQ',
                  '青山不改，綠水長流，後會有期',
                  '十年河東，十年河西，咱們走著瞧 哼']

# flex json files
data_ui_file = open('flex/data_ui.json', mode='r', encoding='utf-8-sig', errors='ignore')

# cache json
setting_file_path = 'database/setting.json'


def data_ui():
    json_obj = json.load(data_ui_file)
    data_ui_file.seek(0)
    return json_obj


def get_setting():
    with open(setting_file_path, mode='r', encoding='utf-8', errors='ignore') as f:
        setting_dict = json.load(f)
        if 'reminder' not in setting_dict:
            setting_dict['reminder'] = {}
        return setting_dict


def put_setting(setting_dict):
    with open(setting_file_path, mode='w', encoding='utf-8', errors='ignore') as f:
        json.dump(setting_dict, f, ensure_ascii=False, indent=4)


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        body_json = json.loads(body)
        event_info = body_json['events'][0]
        user_id = event_info['source']['userId']
        print('[使用者] ' + user_id)
        if event_info['type'] == 'message':
            if event_info['message']['type'] == 'text':
                print('[文字訊息] ' + event_info['message']['text'])
        elif event_info['type'] == 'postback':
            print('[postback data] ' + event_info['postback']['data'])

        handler.handle(body, signature)

    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    msg = event.message.text
    user_id = event.source.user_id

    if msg == ';;update':
        if user_id == ADMIN_ID:
            line_bot_api.broadcast(
                [
                    TextSendMessage(text='資料更新囉，快看看ㄅ'),
                    FlexSendMessage(alt_text='資料庫', contents=data_ui())
                ]
            )
    elif msg == ';;md':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=HACKMD_URL)
        )
    elif msg == ';;drive':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=GOOGLE_DRIVE_URL)
        )
    elif msg == ';;web':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=WEBSITE_URL)
        )
    elif msg == ';;bot':
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text='資料庫', contents=data_ui())
        )
    elif msg.startswith(';;dl') or msg.startswith(';;download'):
        tokens = msg.split()
        if len(tokens) < 3:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='Usage: ;;dl [audio(-a)|video(-v)] [youtube url]')
            )
        media = tokens[1]
        yt_url = tokens[2]
        downloader = Downloader(yt_url)
        temp_store_path = os.path.join('static/', event.source.user_id)

        if media == 'audio' or media == '-a':
            audio_path = downloader.download_audio(audio_type='m4a', output_dir=temp_store_path)
            print(f'{DOMAIN}{audio_path}')
            line_bot_api.reply_message(
                event.reply_token,
                AudioSendMessage(original_content_url=f'{DOMAIN}{audio_path}')
            )
        elif media == 'video' or media == '-v':
            video_path = downloader.download_video(resolution='highest', output_dir=temp_store_path)

            line_bot_api.reply_message(
                event.reply_token,
                VideoSendMessage(original_content_url=f'{DOMAIN}{video_path}')
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='Usage: \n;;dl [audio(-a)|video(-v)] [youtube url]')
            )
    elif msg == ';;bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=random.choice(leave_msg_list)))
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=random.choice(leave_msg_list)))
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='想趕我走就說啦不用還假惺惺的道別(哭泣)'))


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=help_board),
            FlexSendMessage(alt_text='資料庫', contents=data_ui())
        ]
    )


if __name__ == "__main__":
    print('Start running webapp ...')
    app.run()
