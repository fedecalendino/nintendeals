from datetime import datetime

from flask import render_template

from bot.wishlist.constants import ADD_URL
from bot.wishlist.constants import DELETE_URL
from bot.wishlist.constants import SHOW_URL
from commons.config import COUNTRIES
from commons.config import SYSTEMS
from commons.settings import MAINTENANCE
from commons.emoji import NINTENDO
from commons.emoji import PLUS
from commons.emoji import STAR
from commons.emoji import WARNING
from commons.keys import FLAG
from commons.keys import ID
from commons.keys import NAME
from commons.keys import REGION
from commons.keys import SYSTEM
from db.mongo import GamesDatabase


def validate(system, country=None):
    system = SYSTEMS.get(system.title(), SYSTEMS.get(system.upper()))

    if not system:
        raise Exception(f'Invalid system {system}')

    if not country:
        return system, None

    country = COUNTRIES.get(country.upper())

    if not country:
        raise Exception(f'Invalid country {country}')

    return system, country


def index():
    if MAINTENANCE:
        return render_template('maintenance.html')

    return render_template(
        'index.html',
        systems=sorted([system[ID] for system in SYSTEMS.values()]),
        countries=COUNTRIES.values(),
        delete_url=DELETE_URL,
        show_url=SHOW_URL,
        emoji_star=STAR,
        emoji_warning=WARNING
    )


def wishlist(system, country):
    if MAINTENANCE:
        return render_template('maintenance.html')

    try:
        system, country = validate(system, country)
    except:
        return None

    region = country[REGION]
    games = list(GamesDatabase().load_all(
        filter={
            SYSTEM: system[ID],
            f'nsuids.{region}': {'$ne': None},
            'free_to_play': False
        },
        sort=[(f'release_dates.{region}', -1)]
    ))

    for game in games:
        game.countries = []

        for c, d in COUNTRIES.items():
            if d[REGION] in game.nsuids:
                game.countries.append(c)

        game.countries = ' '.join(game.countries)

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
        now=datetime.utcnow(),
        emoji_nintendo=NINTENDO,
        emoji_plus=PLUS,
        emoji_star=STAR,
        emoji_warning=WARNING
    )


def top_wishlist(system, limit=50):
    if MAINTENANCE:
        return render_template('maintenance.html')

    system, _ = validate(system)

    games = GamesDatabase().load_all(
        filter={
            'system': system[ID],
            'free_to_play': False
        },
        sort=[('wishlisted', -1)]
    )

    return render_template(
        'top/wishlist.html',
        games=games,
        limit=limit,
        add_url=ADD_URL,
        show_url=SHOW_URL,
        emoji_plus=PLUS,
        emoji_star=STAR
    )
