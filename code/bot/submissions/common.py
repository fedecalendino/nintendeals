from datetime import datetime

from commons.emoji import ALL_TIME_LOW
from commons.emoji import EXP_TODAY
from commons.emoji import EXP_TOMORROW
from commons.emoji import FIRST_TIME
from commons.emoji import NEW
from commons.emoji import NINTENDO
from commons.emoji import PLAYERS
from commons.emoji import STAR
from commons.settings import WEBSITE_URL

SEPARATOR = '\n___\n'


def header(system=None, country=None, disable_players=False, disable_wishlisted=False):

    header = []

    if system:
        header.append(f'> {NEW} new\n')
        header.append(f'> {FIRST_TIME} first sale\n')
        header.append(f'> {ALL_TIME_LOW} all time low\n')
        header.append(f'> {EXP_TOMORROW} expires tomorrow\n')
        header.append(f'> {EXP_TODAY} expires today\n')
        header.append(f'> {NINTENDO} published by nintendo\n')

        if not disable_wishlisted:
            header.append(f'> {STAR} wishlist count\n')

        if not disable_players:
            header.append(f'> {PLAYERS} max players\n')

        header.append(SEPARATOR)

    return header


def footer(system=None, country=None):
    now = datetime.utcnow()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    time = now.strftime("%H:%M UTC")

    footer = [
        SEPARATOR,
        '* Developed by /u/uglyasablasphemy',
        '  * [Switch Friend Code](https://nin.codes/uglyasablasphemy)',
        '  * [GitHub](https://github.com/federicocalendino/nintendeals)',
        SEPARATOR,
        f'Last update: [{timestamp}](https://google.com/search?q={time})',
        SEPARATOR
    ]

    if system:
        footer.append(f'{STAR} You can add games to your wishlist [HERE]({WEBSITE_URL}/wishlist/{system.lower()}/{country.lower()})')
    else:
        footer.append(f'{STAR} You can add games to your wishlist [HERE]({WEBSITE_URL})')

    return footer

