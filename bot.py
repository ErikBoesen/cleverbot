import os
import requests
import mebots

from flask import Flask, request

app = Flask(__name__)
bot = mebots.Bot('your_bot_shortname_here', os.env['BOT_TOKEN'])

@app.route('/', methods=['GET'])
def home():
    return 'You could put any content here you like, perhaps even a homepage for your bot!'


@app.route('/', methods=['POST'])
def receive():
    data = request.get_json()
    group_id = data["group_id"]
    print('Incoming message:')
    print(data)

    # Prevent self-reply
    if data['sender_type'] != 'bot':
        if data['text'].startswith('/ping'):
            send(data['name'] + ' pinged me!', group_id)

    return 'ok', 200


def send(msg, group_id):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': bot.instance(group_id).id,
        'text': msg,
    }
    r = requests.post(url, data=data)
