from flask import Flask, request, jsonify

import json
import os
from dotenv import load_dotenv

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from datetime import datetime, date

load_dotenv()

PUBLIC_KEY = os.getenv('APP_PUBLIC_KEY')

app = Flask(__name__)

@app.route('/listen', methods=['POST'])
def hello(name=None):
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    signature = request.headers["X-Signature-Ed25519"]
    timestamp = request.headers["X-Signature-Timestamp"]
    body = request.data.decode("utf-8")

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        abort(401, 'invalid request signature')

    if request.json["type"] == 1:
        return jsonify({
            "type": 1
        })
    else:

        parsed_body = json.loads(body)
        options     = parsed_body['data']['options']

        route   = format_route(options[0]['value'])
        stop    = options[1]['value']
        time    = options[2]['value']
        notice  = options[3]['value']

        time_object = datetime.strptime(time, '%H:%M%p')
        today       = date.today()
        time_object = time_object.replace(year=today.year, month=today.month, day=today.day)
        
        return jsonify({
            "type": 4,
            "data": {
                "tts": False,
                "content": f'Great! I will watch the {route} at the {stop} stop and give you {notice} notice to make sure you are on your way by {time}.',
                "embeds": [],
                "allowed_mentions": { "parse": [] }
            }
        })

def format_route( raw_route ):
    if( is_train( raw_route ) ):
        return raw_route.capitalize() + ' Line (Train)'

    return raw_route + ' (Bus)'

def is_train( raw_route ):
    train_lines = [
        'purple',
        'red',
        'yellow',
        'brown',
        'green',
        'orange',
        'pink',
        'blue'
    ]

    if( raw_route.lower() in train_lines ) :
        return True

    return False

# def get_upcoming_trains():

