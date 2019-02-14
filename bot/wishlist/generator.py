from db.mongo import GamesDatabase
from db.mongo import RedditDatabase
from db.mongo import WishlistDatabase

from bot.wishlist.constants import NO_WISHLIST
from bot.wishlist.constants import SEPARATOR
from bot.wishlist.constants import WISHLIST_EMPTY
from bot.wishlist.constants import WL_REMOVE

from commons.config import COUNTRIES
from commons.config import SYSTEMS
from commons.emoji import MINUS
from commons.keys import CURRENCY_CODE
from commons.keys import DIGITS
from commons.keys import DISCOUNT
from commons.keys import END_DATE
from commons.keys import FLAG
from commons.keys import FULL_PRICE
from commons.keys import GAMES
from commons.keys import ID
from commons.keys import SALE_PRICE
from commons.keys import TITLE
from commons.keys import WEBSITES
from commons.settings import REDDIT_USERNAME
from commons.util import format_float


def build_wishlist(username):
    games_db = GamesDatabase()
    wishlist_db = WishlistDatabase()

    wishlist = wishlist_db.load(username)

    if not wishlist:
        return NO_WISHLIST

    if not len(wishlist.get(GAMES, {})):
        return WISHLIST_EMPTY

    content = [
        '',
        'Title | Countries | Actions',
        '--- | --- | :---: '
    ]

    games = {
        game[ID]: game
            for game in games_db.load_all(filter={ID: {'$in': list(wishlist[GAMES].keys())}})
    }

    for game_id, countries in wishlist[GAMES].items():
        game = games[game_id]
        country_list = [f'{COUNTRIES[country][FLAG]} {country}' for country in countries if country in COUNTRIES]

        link = f'[{MINUS}](//reddit.com/message/compose?' \
               f'to={REDDIT_USERNAME}&' \
               f'subject={WL_REMOVE}{SEPARATOR}{game_id}&' \
               f'message=.)'

        content.append('{}|{}|{}'.format(game[TITLE], ' '.join(country_list), link))

    return '\n'.join(content)


def generate_notification(sales_to_notify):
    content = [
        'Title | Expiration | Price | %',
        '--- | --- | --- | --- '
    ]

    for game, price, country, sale in sales_to_notify:
        title = game[TITLE]
        country = COUNTRIES[country]
        end_date = sale[END_DATE].strftime('%b %d')
        sale_price = format_float(sale[SALE_PRICE], country[DIGITS])
        full_price = format_float(price[FULL_PRICE], country[DIGITS])

        if game[WEBSITES].get(country[ID]):
            title = '[{}]({})'.format(title, game[WEBSITES].get(country[ID]))

        content.append(
            f'{title}|'
            f'*{end_date}*|'
            f'{country[FLAG]} **{country[CURRENCY_CODE]} {sale_price}** ~~{full_price}~~|'
            f'{sale[DISCOUNT]}%'
        )

    content.append('')

    return '\n'.join(content)


def generate_header(username):
    return f'##Hi {username}!'


def generate_footer():
    reddit_db = RedditDatabase()

    footer = [
        '',
        f'Add games to your wishlist [HERE]({WISHLIST_URL}).',
        f'Check current deals on {USER_SUBREDDIT}:',
        ''
    ]

    for system in SYSTEMS:
        submission = reddit_db.load(f'{system}/{USER_SUBREDDIT}')

        if submission:
            footer.append(f'* [{system}]({submission[URL]})')

    return '\n'.join(footer)
