from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify
import requests
import json
import re

from misc import *

app = Flask(__name__)
sslify = SSLify(app)

URL = 'https://api.telegram.org/bot{}/'.format(TG_BOT_TOKEN)


def write_json(data, filename='answers.json'):
    with open(filename, 'a') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_message(chat_id, text='blablabla'):
    url = URL + 'sendMessage'
    answer = {
        'chat_id': chat_id,
        'text': text,
    }
    r = requests.post(url, json=answer)
    return r.json()


def parse_user_text(text):
    """Takes user message and looks for a city_name.
    Returns the city name or None.
    """
    pattern = r'/[a-zA-Zа-яА-ЯёЁ]{1,30}[\s-]?[a-zA-Zа-яА-ЯёЁ]{,30}[\s-]?[a-zA-Zа-яА-ЯёЁ]{,30}'
    city_name = re.search(pattern, text)
    if city_name is not None:
        city_name = city_name.group()[1:]
    return city_name


def get_weather(city):
    api_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
    }
    res = requests.get(api_url, params=params)
    data = res.json()

    if data['cod'] == '404':
        return 'Sorry, but I don\'t know any city with "{}" name.'.format(city)
    else:
        weather = int(data['main']['temp'])
        city_name = data['name']
        return "It's {}°C in {} currently.".format(weather, city_name)


@app.route('/{}/'.format(TG_BOT_TOKEN), methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        write_json(r)
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        pattern = r'/[a-zA-Zа-яА-ЯёЁ]{1,30}[\s-]?[a-zA-Zа-яА-ЯёЁ]{,30}[\s-]?[a-zA-Zа-яА-ЯёЁ]{,30}'
        if re.search(pattern, message):
            weather = get_weather(parse_user_text(message))
            send_message(chat_id, text=weather)

        return jsonify(r)

    return '<h1>Bot welcomes you</h1>'


if __name__ == "__main__":
    app.run()