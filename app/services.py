import re
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

from app import db
from models import Chat
from config import URL
from config import WEATHER_API_KEY
from config import OWNER


class Service(ABC):

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass


class Context:

    def __init__(self, service: Service):
        self._service = service

    @property
    def service(self) -> Service:
        return self._service

    @service.setter
    def service(self, service: Service) -> None:
        self._service = service

    def use_service(self, chat_id, message):
        service_answer = self._service.execute(chat_id=chat_id, message=message)
        return service_answer


class Start(Service):

    def execute(self, *args, **kwargs):
        chat_id = int(kwargs.get('chat_id'))
        chat = self._get_chat(chat_id)

        # if chat == 'error':
        #     result = 'Ошибка получения данных'
        # el
        if chat is None:
            result = self._add_chat(chat_id)
        else:
            result = 'Вы уже зарегистрированы'
        return result

    def _add_chat(self, chat_id):
        try:
            chat = Chat(chat_id=chat_id, state='ready')
            db.session.add(chat)
            db.session.commit()
            result = 'Добро пожаловать!'
        except:
            result = 'Ошибка регистрации'
        return result

    def _get_chat(self, chat_id):
        try:
            result = Chat.query.filter(Chat.chat_id==chat_id).first()
        except:
            result = 'error'
        return result


class Weather(Service):

    def execute(self, *args, **kwargs):
        """Contains context logic."""
        chat_id = int(kwargs.get('chat_id'))
        message = kwargs.get('message')
        chat = self._get_chat(chat_id)

        # if chat == 'error':
        #     result = 'Ошибка получения данных'
        # el
        if chat.state == 'ready':
            self._update_chat_state(chat, 'weather')
            result = 'Погода в каком городе интересует?'
        else:
            self._update_chat_state(chat, 'ready')
            result = self.get_weather(message)

        return result

    def _get_chat(self, chat_id):
        try:
            result = Chat.query.filter(Chat.chat_id==chat_id).first()
        except:
            result = 'error'
        return result

    def _update_chat_state(self, chat, state):
        chat.state = state
        db.session.commit()

    def get_weather(self, city):
        """Checks json response and generates response for user.
        May be used independently.
        """
        data = self._get_data(city)
        if data == 'error':
            result = 'Сервис недоступен'
        elif data.get('cod') == '404':
            result = f'К сожалению, я не знаю города с названием "{city}"'
        else:
            try:
                weather = int(data.get('main').get('temp'))
                city_name = data.get('name')
                feels_like = int(data.get('main').get('feels_like'))
                humidity = int(data.get('main').get('humidity'))
                description = data.get('weather')[0].get('description').capitalize()
                clouds = int(data.get('clouds').get('all'))
                wind = int(data.get('wind').get('speed'))

                result = '\n'.join([
                    f'Сейчас {weather}°C в городе {city_name}',
                    f'Ощущается как {feels_like}°C',
                    f'{description}',
                    f'Влажность {humidity}%',
                    f'Облачность {clouds}%',
                    f'Скорость ветра {wind} м/c',
                ])
            except AttributeError:
                result = 'Что-то пошло не так, но скоро это будет исправлено'
            except:
                result = 'Неизвестная ошибка'
        return result

    def _get_data(self, city):
        """Sends request to api and returns json response"""
        api_url = 'http://api.openweathermap.org/data/2.5/weather'
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'lang': 'ru',
        }
        try:
            result = requests.get(api_url, params=params).json()
        except:
            result = 'error'
        return result


class Exrate(Service):

    def __init__(self):
        self.url = 'https://www.cbr-xml-daily.ru/daily_json.js'
        self.valutes = {
            'AUD': 'Australian dollar',
            'GBP': 'Pound sterling',
            'USD': 'United States dollar',
            'EUR': 'Euro',
            'CAD': 'Canadian dollar',
            'CNY': 'Chinese Yuan Renminbi',
            'UAH': 'Ukrainian hryvnia',
            'JPY': 'Japanese yen',
        }

    def execute(self, *args, **kwargs):
        """Returns current exchange rate in rubles for 8 currencies,
        sorted alphabetically.
        """
        data = self._get_data()
        if data == 'error':
            result = 'Сервис недоступен'
        else:
            result = self._generate_response(data)
        return result

    def _get_data(self):
        try:
            result = requests.get(self.url).json()
        except:
            result = 'error'
        return result

    def _generate_response(self, data):
        summary = {}
        for valute, info in data['Valute'].items():
            if valute in self.valutes:
                summary[self.valutes[valute]] = info['Value'] / info['Nominal']
        answer = 'Курс валют на сегодня:\n\n'
        for name in sorted(summary.keys()):
            answer += '{} = {:.2f} rub\n'.format(name, summary[name])
        return answer


class Joke(Service):

    def __init__(self):
        self.joke_url = 'https://bash.im/forweb/?u'

    def execute(self, *args, **kwargs):
        data = self._get_data()
        if data == 'error':
            result = 'Сервис недоступен'
        else:
            result = self._generate_response(data)
        return result

    def _get_data(self):
        try:
            result = requests.get(self.joke_url).text
        except:
            result = 'error'
        return result

    def _generate_response(self, data):
        try:
            data = data.replace("' + '", "")
            html_code = re.search(r'<article(.|\s)*\/article>', data).group()
            soup = BeautifulSoup(html_code, 'lxml')
            result = soup.div.div.get_text("\n") # remove any div to show date
        except:
            result = 'Что-то пошло не так, но скоро это будет исправлено'
        return result


class Translator(Service):

    def __init__(self, word='Hello'):
        self.url = 'https://wooordhunt.ru/word/'
        self.last_word = None
        self.last_url = None
        self.langs = {
            'en': self._parse_en,
            'ru': self._parse_ru,
        }

    def execute(self, *args, **kwargs):
        chat_id = int(kwargs.get('chat_id'))
        message = kwargs.get('message')
        chat = self._get_chat(chat_id)

        # if chat == 'error':
        #     result = 'Ошибка получения данных'
        # el
        if chat.state == 'ready':
            self._update_chat_state(chat, 'translator')
            result = 'Вы зашли в переводчик.\nЗдесь можно узнать перевод слов en-ru/ru-en.\nДля выхода введите "/exit"'
        elif chat.state == 'translator' and message != '/exit':
            result = self.translate(message)
        else:
            self._update_chat_state(chat, 'ready')
            result = 'Вы закрыли переводчик'

        return result

    def _get_chat(self, chat_id):
        try:
            result = Chat.query.filter(Chat.chat_id==chat_id).first()
        except:
            result = 'error'
        return result

    def _update_chat_state(self, chat, state):
        chat.state = state
        db.session.commit()


    def translate(self, word):
        """Contains some validation and parsing base.
        May be used independently.
        """
        self.last_word = word.strip().lower()
        self.last_url = f'{self.url}{self.last_word}'
        lang = self.detect_lang(word.lower())
        html = self._get_html()
        if lang == 'error':
            result = 'Слово должно быть на английском или русском языке'
        elif html == 'error':
            result = 'Сервис недоступен'
        else:
            s = BeautifulSoup(html, 'lxml')
            result = self.langs[lang](s)
        return result

    def _get_html(self):
        try:
            result = requests.get(self.last_url).text
        except:
            result = 'error'
        return result

    def _parse_ru(self, soup):
        try:
            content = soup.find('div', class_='ru_content')
            meaning = [tag.text for tag in content.find_all('a', recursive=False)]
            return f'Основные значения: {", ".join(meaning)}\n\nПодробнее: {self.last_url}'
        except:
            return f'По запросу "{self.last_word}" ничего не найдено'

    def _parse_en(self, soup):
        try:
            content = soup.find('div', id='content_in_russian')
            meaning = content.find('div', class_='t_inline_en').text
            # headers = [header.text.split()[0] for header in content.find_all('h4')]
            # print(headers)
            return f'Основные значения: {meaning}\n\nПодробнее: {self.last_url}'
        except:
            return f'По запросу "{self.last_word}" ничего не найдено'

    def detect_lang(self, word):
        """Checks if the language is English or Russian.
        May be used independently.
        """
        lang = None
        for letter in word:
            n = ord(letter)
            if 96 < n < 123 or n == 39 or n == 45:
                if lang == 'en':
                    continue
                elif lang is None:
                    lang = 'en'
                else:
                    lang = 'error' # At least one latin character among cyrillic
                    break
            elif 1071 < n < 1104 or n == 1105:
                if lang == 'ru':
                    continue
                elif lang is None:
                    lang = 'ru'
                else:
                    lang = 'error' # At least one cyrillic character among latin
                    break
            else:
                lang = 'error' # Irrelevant symbols
                break
        return lang


class ParsedRequest:

    def __init__(self, request):
        self.r = request
        try:
            self.chat_id = self.get_chat_id()
            self.message = self.get_message()
        except:
            self.chat_id = OWNER
            self.message = 'fixed'

    def get_message(self):
        return self.r.get('message').get('text')

    def get_chat_id(self):
        return self.r.get('message').get('chat').get('id')

    def get_usern(self):
        return self.r.get('message').get('chat').get('username')

    def get_firstn(self):
        return self.r.get('message').get('chat').get('first_name')

    def get_lastn(self):
        return self.r.get('message').get('chat').get('last_name')


class ServiceManager:

    def __init__(self):
        self.services = {
            '/start': Start,
            '/weather': Weather,
            '/exrate': Exrate,
            '/joke': Joke,
            '/translator': Translator,
        }
        self.chat_id = self.message = self.service = None

    def set_attrs(self, parsed_req):
        self.chat_id = parsed_req.chat_id
        self.message = parsed_req.message
        self.service = self._get_service()

    def _clear_attrs(self):
        self.chat_id = self.message = self.service = None

    def _get_service(self):
        service = self.services.get(self.message)
        state = self._get_chat_state(int(self.chat_id))

        if service is None and state == 'ready':
            result = None
        elif service is not None and state == 'ready':
            result = service()
        else:
            service = self.services.get(f'/{state}')
            result = service()

        return result

    def _get_chat_state(self, chat_id):
        try:
            result = Chat.query.filter(Chat.chat_id==chat_id).first().state
        except AttributeError:
            result = 'start'
        return result

    def use_service(self):
        if self.service is not None:
            context = Context(self.service)
            context_answer = context.use_service(
                self.chat_id,
                self.message
            )
            self.send_message(self.chat_id, text=context_answer)
            self._clear_attrs()

    def send_message(self, chat_id, text='<default text>'):
        url = URL + 'sendMessage'
        answer = {
            'chat_id': chat_id,
            'text': text,
        }
        r = requests.post(url, json=answer)
        return r.json()