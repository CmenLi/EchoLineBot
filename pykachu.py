from __future__ import unicode_literals

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import random

import configparser
import json

import clock
from clock import *


app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# variables
# const:
ADMIN_ID = 'U940d15d3a94c5e90dde5e52dd373d0be'

HACKMD_URL = 'https://hackmd.io/@KoiSharp/H1l7A7kRI'
GOOGLE_DRIVE_URL = 'https://drive.google.com/drive/folders/13YSMSTgxpUFwUzXafZbvlbZk89yJPvNF?usp=sharing'
WEBSITE_URL = 'https://pykachu-website.herokuapp.com/resources.jsp'

help_board = '========小幫手========\n' \
             ';;bot   - 功能介面\n' \
             ';;md    - 查看HackMD筆記\n' \
             ';;drive - 查看共享資料\n' \
             ';;web   - 查看網站(比賽資料)\n' \
             ';;bye   - 掰掰'

leave_msg_list = ['掰掰♪ 有需要再找我呦~',
                  '怎麼趕我走! QAQ',
                  '青山不改，綠水長流，後會有期',
                  '十年河東，十年河西，咱們走著瞧 哼']

# flex json files
data_ui_file = open('flex/data_ui.json', mode='r', encoding='utf-8-sig', errors='ignore')
reminder_ui_file = open('flex/reminder_datetime_ui.json', mode='r', encoding='utf-8-sig', errors='ignore')
remind_confirm_ui_file = open('flex/remind_confirm_ui.json', mode='r', encoding='utf-8-sig', errors='ignore')

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
    elif msg == ';;remind':
        reminder_ui = json.load(reminder_ui_file)
        reminder_ui_file.seek(0)
        reminder_msg = FlexSendMessage(alt_text='Reminder', contents=reminder_ui)
        line_bot_api.reply_message(
            event.reply_token,
            reminder_msg
        )
        pass
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
    else:
        setting_dict = get_setting()
        reminder_setting_dict = setting_dict['reminder']
        if user_id in reminder_setting_dict.keys():
            e_dict = reminder_setting_dict[user_id]
            e_dict['item'] = msg
            put_setting(setting_dict)

            remind_confirm_ui = json.load(remind_confirm_ui_file)
            remind_confirm_ui_file.seek(0)  # when json object was loaded, we should reset the read cursor.

            remind_content = remind_confirm_ui['body']['contents'][1]['contents']
            remind_content[0]['contents'][1]['contents'][0]['text'] = e_dict['date_time']
            remind_content[1]['contents'][1]['contents'][0]['text'] = e_dict['item']

            remind_confirm_ui_msg = FlexSendMessage(
                alt_text='Reminder confirmation page',
                contents=remind_confirm_ui
            )
            line_bot_api.reply_message(
                event.reply_token,
                remind_confirm_ui_msg
            )


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=help_board),
            FlexSendMessage(alt_text='資料庫', contents=data_ui())
        ]
    )


@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data = event.postback.data
    setting_dict = get_setting()
    reminder_setting_dict = setting_dict['reminder']

    if data == 'reminder_datetime_postback':
        scheduled_event = ScheduledEvent(event.postback.params['datetime'], '(None)')

        reminder_setting_dict[user_id] = scheduled_event.__dict__
        put_setting(setting_dict)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='請輸入文字訊息以設定提醒事項')
        )
    elif data == 'reminder_confirm_ok':
        if user_id in reminder_setting_dict.keys():
            e_dict = reminder_setting_dict[user_id]
            e = ScheduledEvent(e_dict['date_time'], e_dict['item'])
            clock.set_notify(user=user_id, event=e)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='收到!! 將在 ' + e.date_time + ' 時提醒你')
            )
            reminder_setting_dict.pop(user_id, None)
            put_setting(setting_dict)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='這個提醒你已經設定過囉')
            )
    elif data == 'reminder_confirm_cancel':
        if user_id in reminder_setting_dict.keys():
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='已取消這次的設定')
            )
            reminder_setting_dict.pop(user_id, None)
            put_setting(setting_dict)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='這個提醒你已經設定過囉')
            )


if __name__ == "__main__":
    print('Start running webapp ...')
    app.run()
