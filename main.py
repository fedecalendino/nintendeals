# Standard
import logging
import time
import threading

# Requirements
import requests
from flask import Flask
from flask_cors import CORS

# Modules
from app import bot
from app.commons.config import PORT
from app.services import games, config


LOG = logging.getLogger('main')


def register_blueprint(app, blueprint):
    app.register_blueprint(blueprint, url_prefix=blueprint.prefix)


api = Flask(__name__)
CORS(api)

register_blueprint(api, games.blueprint)
register_blueprint(api, config.blueprint)


@api.before_first_request
def activate_job():
    def run_job():
        while True:
            bot.main()

            time.sleep(3)

    thread = threading.Thread(target=run_job)
    thread.start()


@api.route("/heartbeat")
def hello():
    return "🌿 Yahaha! You found me! 🌿"


def start_runner():
    def start_loop():
        not_started = True

        while not_started:
            print('Checking if server is alive...')

            try:
                r = requests.get('http://0.0.0.0:{}/heartbeat'.format(PORT))

                if r.status_code == 200:
                    print('Server started...')
                    not_started = False

                print(r.status_code)
            except:
                print('Server not yet started...')

            time.sleep(1)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    start_runner()

    api.run(host='0.0.0.0', port=PORT)

