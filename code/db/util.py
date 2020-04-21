from commons.config import COUNTRIES
from commons.keys import SYSTEM
from db.mongo import GamesDatabase
from db.mongo import PricesDatabase


def get_games_on_sale(system=None):
    games_db = GamesDatabase()
    prices_db = PricesDatabase()

    filter = {} if not system else {SYSTEM: system}

    deals = {price.id: price for price in prices_db.load_all(filter=filter)
             if any([price.prices[country].active for country in COUNTRIES if price.prices.get(country)])}
    games = {game.id: game for game in games_db.load_all(filter=filter)
             if any([nsuid for nsuid in game.nsuids.values() if nsuid in deals])}

    games = dict(sorted(games.items(), key=lambda kv: kv[1].title.lower()))

    return games, deals
