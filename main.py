# Standard
import logging
import time
import threading

# Requirements
import requests
from flask import Flask
from flask import send_from_directory
from flask_cors import CORS

# Modules
from bot import bot
from bot.commons.config import IP, PORT
from api import games, config


LOG = logging.getLogger('main')


def register_blueprint(application, blueprint):
    application.register_blueprint(blueprint, url_prefix=blueprint.prefix)


app = Flask(__name__)
CORS(app)

# Api =========================================================================


@app.route("/heartbeat")
def hello():
    return "🌿 Yahaha! You found me! 🌿"


register_blueprint(app, games.blueprint)
register_blueprint(app, config.blueprint)

# Web =========================================================================


@app.route("/")
@app.route("/wishlist")
@app.route("/wishlist/")
def wishlist():
    return send_from_directory('web', 'wishlist.html')


@app.route('/css/<path:path>')
@app.route('/wishlist/css/<path:path>')
def send_css(path):
    return send_from_directory('web/css', path)


@app.route('/js/<path:path>')
@app.route('/wishlist/js/<path:path>')
def send_js(path):
    return send_from_directory('web/js', path)


# Bot =========================================================================
@app.before_first_request
def activate_job():
    def run_job():
        while True:
            bot.main()

            time.sleep(3)

    thread = threading.Thread(target=run_job)
    thread.start()


def start_runner():
    def start_loop():
        not_started = True

        while not_started:
            print('Checking if server is alive...')

            try:
                r = requests.get('http://{}:{}/heartbeat'.format(IP, PORT))

                if r.status_code == 200:
                    print('Server started...')
                    not_started = False

                print(r.status_code)
            except:
                print('Server not yet started...')

            time.sleep(1)

    print('Started runner')
    threading.Thread(target=start_loop).start()


# Main ========================================================================


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    start_runner()

    app.run(host=IP, port=PORT)

