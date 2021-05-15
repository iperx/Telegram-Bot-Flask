from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
from flask_script import Manager

from config import Configuration


### App init ###
app = Flask(__name__)
app.config.from_object(Configuration)

### ORM ###
db = SQLAlchemy(app)

### Database migrations ###
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)