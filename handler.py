import sys
sys.path.insert(0, 'vendor')

import json
import os
import argparse
import requests
import func_timeout


PREFIX = '.'
TIMEOUT_ERROR_MESSAGE = 'Cleverbot API appears to be offline. If cleverbot.io is online, something may have gone wrong. Open an issue at https://github.com/ErikBoesen/cleverbot/issues/new if so.'

class CleverBot:
    _API_ROOT = 'https://cleverbot.io/1.0/'

    def __init__(self, user, key, group_id):
        self.user = user
        self.key = key
        self.nick = f'GroupMe_{group_id}'

        body = {
            'user': user,
            'key': key,
            'nick': self.nick
        }
        requests.post(self._API_ROOT + 'create', data=body)

    def query(self, text):
        body = {
            'user': self.user,
            'key': self.key,
            'nick': self.nick,
            'text': text
        }

        r = requests.post(self._API_ROOT + 'ask', data=body)
        if not r.ok:
            return TIMEOUT_ERROR_MESSAGE
        r = r.json()

        if r['status'] == 'success':
            return r['response']
        else:
            return None


def receive(event, context):
    data = json.loads(event['body'])
    group_id = data['group_id']
    bot_id = data['bot_id']

    # Prevent self-reply
    if data['sender_type'] != 'bot':
        if data['text'].startswith(PREFIX):
            print('Received:')
            print(data)
            Thread(target=reply, args=(data['text'][len(PREFIX):].strip(), group_id)).start()

    return {
        'statusCode': 200,
        'body': 'ok'
    }


def get_response(text, group_id):
    client = CleverBot(os.environ.get('CLEVERBOT_USER'), os.environ.get('CLEVERBOT_KEY'), group_id)
    return client.query(text)


def reply(text, bot_id):
    try:
        reply_text = func_timeout.func_timeout(max_wait, lambda: get_response(text, bot_id))
    except func_timeout.FunctionTimedOut:
        reply_text = TIMEOUT_ERROR_MESSAGE
    send(reply_text, bot_id)


def send(msg, bot_id):
    url = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': bot_id,
        'text': msg,
    }
    r = requests.post(url, json=data)
