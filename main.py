import logging
import threading
import time

import requests
from flask import Flask
from flask import redirect
from flask import send_from_directory
from flask_cors import CORS

import api
from bot.jobs import inbox
from web import generator

from commons.settings import IP
from commons.settings import PORT


LOG = logging.getLogger('main')


def register_blueprint(application, blueprint):
    application.register_blueprint(blueprint, url_prefix=blueprint.prefix)


app = Flask(__name__)
CORS(app)

# Api =========================================================================


@app.route("/heartbeat")
def hello():
    return "🌿 Yahaha! You found me! 🌿"


register_blueprint(app, api.jobs.blueprint)


# Web =========================================================================


@app.route("/")
def root():
    return generator.index()


@app.route("/index.html")
def index():
    return generator.index()


@app.route("/wishlist/<string:system>/<string:country>")
def wishlist(system, country):
    response = generator.wishlist(system, country)

    if not response:
        return redirect("/", code=302)
    else:
        return response


# Web Resources ===============================================================


@app.route("/favicon.ico")
def favicon():
    return send_from_directory('web', 'favicon.ico')


@app.route('/<string:resource>/<path:path>')
def css(resource, path):
    if resource in ['css', 'img', 'js']:
        return send_from_directory(f'web/{resource}', path)
    else:
        return None


# Bot =========================================================================

@app.before_first_request
def activate_job():
    def run_job():
        while True:
            inbox.check()

            time.sleep(15)

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

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=IP, port=PORT)

