# Standard
from datetime import datetime

# Dependencies
from flask import request
from flask import Blueprint
from flask import Response

# Modules
from bot.db.util import load_games
from bot.commons.util import format_float

# Statics
from bot.commons.config import *
from bot.commons.keys import *

TAG = 'prices'

blueprint = Blueprint('services.prices', __name__)
blueprint.prefix = "/api/v1/prices"


@blueprint.route('/<game_id>', methods=['GET'])
def price(game_id):
    now = datetime.utcnow()

    games = load_games(filter={id_: game_id})

    if len(games) == 0:
        return Response('Invalid game id', 404)

    game = games[0]

    text = [
        'Title | Expiration | Price | % ',
        '--- | --- | --- | --- '
    ]

    for country, details in game[prices_].items():
        title = game[title_]

        country_details = COUNTRIES[country]

        last_sale = details[sales_][-1]

        if last_sale[start_date_] < now < last_sale[end_date_]:
            currency = country_details[currency_code_]
            sale_price = format_float(last_sale[sale_price_], 0)
            full_price = format_float(details[full_price_], 0)
            discount = last_sale[discount_]

            if websites_ in game:
                if country in game[websites_]:
                    title = '[{}]({})'.format(
                        title, game[websites_][country].replace('https://www.', '//'))

            # Creating row
            text.append(
                '{title}|*{end_date}*|{flag} **{currency} {sale_price}** ~~{full_price}~~|`%{discount}`'.format(
                    title=title, end_date=last_sale[end_date_].strftime("%b %d"), flag=country_details[flag_],
                    currency=currency, sale_price=sale_price, full_price=full_price, discount=discount)
            )

    return Response(
        '\n'.join(text),
        mimetype="text/plain")



