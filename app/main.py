from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify
import requests
import json
import re

from misc import TG_BOT_TOKEN
from misc import WEATHER_API_KEY
from task import Task

app = Flask(__name__)
sslify = SSLify(app)
URL = 'https://api.telegram.org/bot{}/'.format(TG_BOT_TOKEN)
tasks = {} # "chat_id": task
chat_members = set() # new
bot_commands = {'/weather', '/exrate', '/join', '/exit', '/whoisup'}


def write_json(data, filename='answers.json'):
    """Dumps json data to a file.
    """
    with open(filename, 'a') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_message(chat_id, text='blablabla'):
    """Sends the text message to the particular private chat.
    """
    url = URL + 'sendMessage'
    answer = {
        'chat_id': chat_id,
        'text': text,
    }
    r = requests.post(url, json=answer)
    return r.json()


def parse_user_text(text):
    """Takes user's text message and looks for a city_name.
    Returns the city name or None.
    """
    pattern = r'^[a-zA-Zа-яА-ЯёЁ]{1,30}[\s-]?[a-zA-Zа-яА-ЯёЁ]{,30}[\s-]?[a-zA-Zа-яА-ЯёЁ]{,30}'
    weather_query = re.search(pattern, text)
    if weather_query is not None:
        city_name = weather_query.group()
        return city_name


def get_weather(city):
    """Takes the city name.
    Returns current weather in degrees Celsius or the message,
    saying that the required city hasn't been found.
    """
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


def get_exchange_rate():
    """Returns current exchange rate in rubles for 8 currencies,
    sorted alphabetically.
    """
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    summary = {}
    valutes = {
        'AUD': 'Australian dollar', 
        'GBP': 'Pound sterling', 
        'USD': 'United States dollar', 
        'EUR': 'Euro', 
        'CAD': 'Canadian dollar', 
        'CNY': 'Chinese Yuan Renminbi', 
        'UAH': 'Ukrainian hryvnia', 
        'JPY': 'Japanese yen',
        }
    res = requests.get(url).json()
    for valute, info in res['Valute'].items():
        if valute in valutes:
            summary[valutes[valute]] = info['Value'] / info['Nominal']
            
    answer = '>This is what we have today:\n\n'
    for name in sorted(summary.keys()):
        answer += '{} = {:.2f} rub\n\n'.format(name, summary[name])

    return answer.rstrip()


def send_msg_to_all(user, message, m_type='normal'):
    """Sends the message to chat users.
    The argument 'm_type':
    'system' - for system messages
    'normal' - for regular messages from one user to all others except himself
    """
    if m_type == 'system':
        for person in chat_members:
            text = '*{} {}*'.format(user['first_name'], message)
            send_message(person, text=text)
    else:
        for person in chat_members:
            if person != user['id']:
                text = user['first_name'] + ':\n' + message
                send_message(person, text=text)


@app.route('/{}/'.format(TG_BOT_TOKEN), methods=['POST', 'GET'])
def index():
    """Reacts to all the possible commands.
    I know this function does almost everything TODO: fix it ASAP
    """
    if request.method == 'POST':
        r = request.get_json()
        if 'text' in r['message']:
            chat_id = r['message']['chat']['id']
            message = r['message']['text']
            user = r['message']['from']

            if user['id'] in chat_members and message not in bot_commands:
                send_msg_to_all(user, message)

            if chat_id not in tasks:
                if message == '/weather':
                    task = Task(chat_id, 'weather')
                    send_message(task.chat_id, text='The weather in which city is interesting to you?')
                    tasks[task.chat_id] = task
                elif message == '/exrate':
                    exrate = get_exchange_rate()
                    send_message(chat_id, text=exrate)
                elif message == '/join':
                    if user['id'] not in chat_members:
                        chat_members.add(user['id'])
                        send_msg_to_all(user, 'enters the chat', 'system')
                elif message == '/exit':
                    chat_members.discard(user['id'])
                    send_msg_to_all(user, 'leaves the chat', 'system')
                elif message == '/whoisup':
                    ids_up = '\n'.join([str(m) for m in chat_members])
                    send_message(chat_id, text=ids_up)
            else:
                task = tasks[chat_id]
                if task.message == 'weather':
                    city = parse_user_text(message)
                    if city is not None:
                        weather = get_weather(city)
                        send_message(task.chat_id, text=weather)
                    else:
                        send_message(task.chat_id, text='Incorrect city name.')
                    tasks.pop(chat_id, None)

        return jsonify(r)

    return '<h1>Bot welcomes you</h1>'


if __name__ == "__main__":
    app.run()