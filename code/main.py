# pragma: no cover

import logging
import time
from threading import Thread

import requests
from flask import Flask
from flask import redirect
from flask import request
from flask import send_from_directory
from flask_cors import CORS

import api
from bot.jobs import inbox
from bot.jobs.main import check_last_update
from bot.reddit import Reddit
from cache import cache
from commons.settings import IP
from commons.settings import PORT
from web import generator

LOG = logging.getLogger('main')


def register_blueprint(application, blueprint):
    application.register_blueprint(blueprint, url_prefix=blueprint.prefix)


app = Flask(__name__)
CORS(app)
cache.init_app(app, config={"CACHE_TYPE": "simple"})


# Api =========================================================================


@app.route("/heartbeat")
def hello():
    return "🌿 Yahaha! You found me! 🌿"


register_blueprint(app, api.games.blueprint)
register_blueprint(app, api.jobs.blueprint)


# Web =========================================================================


@app.route("/")
def root():
    return generator.index()


@app.route("/index.html")
def index():
    return generator.index()


@app.route("/wishlist/<string:system>/<string:country>")
@cache.cached(timeout=60 * 60)
def wishlist(system, country):
    response = generator.wishlist(system, country)

    if not response:
        return redirect("/", code=302)
    else:
        return response


@app.route("/top/wishlist/<string:system>")
def top_wishlist(system):
    limit = int(request.args.get('limit', '50'))
    response = generator.top_wishlist(system, limit)

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
        last_update_thread = Thread(target=check_last_update)
        last_update_thread.start()

        while True:
            try:
                inbox.check()
                time.sleep(10)
            except Exception as exc:
                LOG.error(exc)
                time.sleep(15)

    run_job_thread = Thread(target=run_job)
    run_job_thread.start()


def start_runner():
    def start_loop():
        not_started = True

        while not_started:
            print('Checking if server is alive...')

            try:
                r = requests.get(f'http://{IP}:{PORT}/heartbeat')

                if r.status_code == 200:
                    print('Server started...')
                    not_started = False

                print(r.status_code)
            except:
                print('Server not yet started...')

            time.sleep(1)

    print('Started runner')
    start_loop_thread = Thread(target=start_loop)
    start_loop_thread.start()


# Main ========================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    start_runner()

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=IP, port=PORT)

