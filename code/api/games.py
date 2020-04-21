from flask import Blueprint
from flask import jsonify

from api.util import validate_public_key
from cache import cache
from db.util import get_games_on_sale

from commons.config import COUNTRIES
from commons.config import SYSTEMS
from commons.keys import ID

TAG = 'games'

blueprint = Blueprint(TAG, __name__)
blueprint.prefix = f"/api/{TAG}"


@blueprint.route('/<string:system>', methods=['GET'])
@cache.cached(timeout=60 * 60)
def list_games(system):
    message = validate_public_key()

    if message:
        return message

    system = SYSTEMS.get(system.title(), SYSTEMS.get(system.upper()))

    if not system:
        raise Exception(f'Invalid system {system}')

    games, prices = get_games_on_sale(system=system[ID])

    tmp_games = []

    for game_id, game in games.items():
        tmp_prices = {}

        for region, nsuid in game.nsuids.items():
            game_prices = prices.get(nsuid)

            if not game_prices:
                continue

            for country, price in game_prices.prices.items():

                if not price:
                    continue

                tmp_prices[country] = {
                    'currency': price.currency,
                    'full_price': price.full_price,
                }

                if price.active:
                    tmp_prices[country]['sale_price'] = price.active.sale_price
                    tmp_prices[country]['end_date'] = str(price.active.end_date)
                    tmp_prices[country]['discount'] = price.active.discount

        tmp_game = {
            'titles': game.titles,
            'nsuids': game.nsuids,
            'release_dates': game.release_date,
            'price': tmp_prices,
            'scores': {
                'metascore': game.scores.metascore,
                'userscore': game.scores.userscore,
            },
            'published_by_nintendo': game.published_by_nintendo,
            'wishlist_count': game.wishlisted
        }

        tmp_games.append(tmp_game)

    output = {
        'countries': COUNTRIES,
        'games_on_sale': tmp_games,
    }

    return jsonify(output)

