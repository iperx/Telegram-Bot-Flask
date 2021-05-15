# Telegram-Bot-Flask

## Description

The bot is made to show:

* current weather in any city
* today's exchange rate (for 10 currencies)
* jokes from a good old [bash.org](https://bash.im/)

It can also translate single words en-ru/ru-en.

### Tools:

* Python 3.8+
* Flask 1.1.2
* SQLAlchemy 1.3.23
* Flask-Migrate 2.6.0
* MySQL 5.7 or 8.0
* Beautifulsoup4 4.9.3

### Commands:
* /weather ([source](https://openweathermap.org/api/))
* /exrate ([source](https://www.cbr-xml-daily.ru/))
* /joke ([source](https://bash.im/))
* /translator ([source](https://wooordhunt.ru/))

## Customization
1. Create your bot with @BotFather and you will receive a _bot token_
2. Sign up [here](https://openweathermap.org/api/) to receive a _weather API token_
3. Find out your Telegram ID to use it as an _Owner ID_ (messages about the start will be sent there)
4. Make sure that _mysql-server_ and _libmysqlclient-dev_ are installed on your system
5. Create a new MySQL database for bot
6. Clone this repository into your system
7. Install required packages (I personally prefer pipenv):
    
    `pipenv install && pipenv shell`
8. Open **config.py** in a text editor to set up your tokens, owner id and database fields (username, password, hostname, databasename)
9. Don't forget to make database migrations:
    ```
    python3 manage.py db init
    python3 manage.py db migrate
    python3 manage.py db upgrade
    ```
10. Set webhook using request like this:
https://api.telegram.org/botYOUR_TOKEN/setWebhook?url=https://YOUR_DOMAIN/YOUR_TOKEN
11. Launch file **bot.py** to start