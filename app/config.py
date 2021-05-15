### Constants ###
TG_BOT_TOKEN = "your_token"
WEATHER_API_KEY = "your_api_key"
OWNER = "your_id"
URL = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/'


class Configuration:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="your_db_username",
        password="your_db_password",
        hostname="your_hostname",
        databasename="your_db_name",
    )
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False