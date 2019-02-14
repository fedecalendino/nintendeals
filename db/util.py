from datetime import datetime

from db.mongo import GamesDatabase
from db.mongo import PricesDatabase

from commons.config import COUNTRIES
from commons.keys import END_DATE
from commons.keys import ID
from commons.keys import LATEST_SALE
from commons.keys import NSUIDS
from commons.keys import START_DATE
from commons.keys import SYSTEM


def get_latest_sale(price):
    if not price:
        return None

    latest_sale = price.get(LATEST_SALE)

    if not latest_sale:
        return None

    return latest_sale if latest_sale[START_DATE] < datetime.utcnow() < latest_sale[END_DATE] else None


def get_games_on_sale(system=None):
    games_db = GamesDatabase()
    prices_db = PricesDatabase()

    filter = {} if not system else {SYSTEM: system}

    deals = {price[ID]: price for price in prices_db.load_all(filter=filter)
             if any([get_latest_sale(price.get(country)) for country in COUNTRIES])}
    games = {game[ID]: game for game in games_db.load_all(filter=filter)
             if any([nsuid for nsuid in game[NSUIDS].values() if nsuid in deals])}

    return games, deals
