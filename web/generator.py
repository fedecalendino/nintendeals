from flask import render_template

from db.mongo import GamesDatabase

from bot.wishlist.constants import ADD_URL
from bot.wishlist.constants import SHOW_URL
from bot.wishlist.constants import DELETE_URL

from commons.config import COUNTRIES
from commons.config import SYSTEMS

from commons.emoji import NINTENDO
from commons.emoji import PLUS
from commons.emoji import STAR
from commons.emoji import WARNING

from commons.keys import ID
from commons.keys import FLAG
from commons.keys import NAME
from commons.keys import REGION
from commons.keys import SYSTEM


def validate(system, country):
    system = SYSTEMS.get(system.title(), SYSTEMS.get(system.upper()))
    country = COUNTRIES.get(country.upper())

    if not system:
        raise Exception(f'Invalid system {system}')

    if not country:
        raise Exception(f'Invalid country {country}')

    return system, country


def wishlist(system, country):
    try:
        system, country = validate(system, country)
    except:
        return None

    region = country[REGION]
    games = GamesDatabase().load_all(
        filter={
            SYSTEM: system[ID],
            f'nsuids.{region}': {'$ne': None}
        },
        sort=[(f'release_dates.{region}', -1)]
    )

    return render_template(
        'wishlist.html',
        system=system[NAME],
        country=country[ID],
        flag=country[FLAG],
        region=region,
        games=games,
        add_url=ADD_URL,
        delete_url=DELETE_URL,
        show_url=SHOW_URL,
        emoji_nintendo=NINTENDO,
        emoji_plus=PLUS,
        emoji_star=STAR,
        emoji_warning=WARNING
    )


def index():
    return render_template(
        'index.html',
        systems=SYSTEMS.values(),
        countries=COUNTRIES.values(),
        delete_url=DELETE_URL,
        show_url=SHOW_URL,
        emoji_star=STAR,
        emoji_warning=WARNING
    )
