# Telegram-Bot-Flask

* Tells what's the weather in any city at the moment
* Gives the today's exchange rate
* Contains the simple chat for users

### Weather
**Source**: <https://openweathermap.org/api>
**Commands**:
* /weather

### Exchange rate
**Source**: <https://www.cbr-xml-daily.ru/>
**Commands**:
* /exrate

### Chat
**Commands**:
* /join
* /exit
* /whoisup

### Customization:
1. Create your bot with @BotFather (you'll receive a token)
2. Register an account on the weather website and receive an API token
3. Create file _misc.py_ in the _app_ folder beside the _main.py_
4. Put `TG_BOT_TOKEN = 'your-bot-token'` into the _misc.py_
5. Put `WEATHER_API_KEY = 'your-weather-token'` down below
6. Get hosting (e.g. <https://www.pythonanywhere.com/>)
