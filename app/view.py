from flask import request
from flask import jsonify

from app import app
from config import TG_BOT_TOKEN
from config import OWNER
import services


### Service manager init ###
manager = services.ServiceManager()
manager.send_message(OWNER, '<System>: Bot is running')


@app.route(f'/{TG_BOT_TOKEN}', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        pr = services.ParsedRequest(r)
        manager.set_attrs(pr)
        manager.use_service()

        return jsonify(r)
    return '<h1>Bot welcomes you.</h1>'