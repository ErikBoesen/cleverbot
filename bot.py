import os
import argparse
import requests
import mebots
import json

from flask import Flask, request

app = Flask(__name__)
bot = mebots.Bot('your_bot_shortname_here', os.environ.get('BOT_TOKEN'))

class CleverBot:
    def __init__(self, user, key, group_id):
        self.user = user
        self.key = key
        self.nick = f"GroupMe_{group_id}"

        body = {
            "user": user,
            "key": key,
            "nick": self.nick
        }
        requests.post("https://cleverbot.io/1.0/create", data=body)

    def query(self, text):
        body = {
            "user": self.user,
            "key": self.key,
            "nick": self.nick,
            "text": text
        }

        r = requests.post("https://cleverbot.io/1.0/ask", data=body)
        r = json.loads(r.text)

        if r["status"] == "success":
            return r["response"]
        else:
            return None

@app.route('/', methods=['GET'])
def home():
    return 'You could put any content here you like, perhaps even a homepage for your bot!'

PREFIX = '.'
clients = {}

def get_response(text, group_id):
    if clients.get(group_id) is None:
        clients[group_id] = CleverBot(os.environ.get("CLEVERBOT_USER"), os.environ.get("CLEVERBOT_KEY"), group_id)
    return clients[group_id].query(text)

@app.route('/', methods=['POST'])
def receive():
    data = request.get_json()
    group_id = data.get("group_id")
    print('Incoming message:')
    print(data)

    # Prevent self-reply
    if data['sender_type'] != 'bot':
        if data['text'].startswith(PREFIX):
            send(data['text'][len(PREFIX):].strip(), group_id)

    return 'ok', 200


def send(msg, group_id):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': bot.instance(group_id).id,
        'text': msg,
    }
    r = requests.post(url, data=data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?")
    args = parser.parse_args()
    if args.command:
        print(get_response({'text': args.command, 'sender_type': 'bot'}, 0))
    else:
        while True:
            print(get_response({'text': input("> "), 'sender_type': 'bot'}, 0))
