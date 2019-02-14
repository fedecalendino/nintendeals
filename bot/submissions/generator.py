from datetime import datetime

from db.util import get_latest_sale

from commons.config import COUNTRIES
from commons.emoji import EXP_TODAY
from commons.emoji import EXP_TOMORROW
from commons.emoji import NEW
from commons.emoji import NINTENDO
from commons.keys import CURRENCY
from commons.keys import DIGITS
from commons.keys import DISCOUNT
from commons.keys import END_DATE
from commons.keys import FLAG
from commons.keys import FULL_PRICE
from commons.keys import ID
from commons.keys import METASCORE
from commons.keys import NAME
from commons.keys import NSUIDS
from commons.keys import NUMBER_OF_PLAYERS
from commons.keys import REGION
from commons.keys import SALE_PRICE
from commons.keys import SCORES
from commons.keys import START_DATE
from commons.keys import SYSTEM
from commons.keys import TITLE
from commons.keys import URL
from commons.keys import USERSCORE
from commons.keys import WEBSITES
from commons.util import format_float


SEPARATOR = '\n___\n'


def generate_header():
    return [
        f'>`{NEW} new` `{EXP_TOMORROW} expires tomorrow` `{EXP_TODAY} expires today` `{NINTENDO} published by nintendo`',
        SEPARATOR
    ]


def generate_footer():
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    return [
        SEPARATOR,
        '* Developed by /u/uglyasablasphemy | [Switch Friend Code](https://nin.codes/uglyasablasphemy)',
        '* Use [RES](https://redditenhancementsuite.com) for table sorting and more',
        '* If you have perfomance issues, you might want to check out:',
        '   * [Reddit is Fun](https://play.google.com/store/apps/details?id=com.andrewshu.android.reddit)',
        '   * [Apollo for Reddit](https://itunes.apple.com/us/app/apollo-for-reddit/id979274575)',
        SEPARATOR,
        f'Last update: {timestamp}'
    ]


def make_row(game, country, price, sale, disable_urls=False):
    now = datetime.utcnow()

    title = game[TITLE][1:] if game[TITLE].startswith(' ') else game[TITLE]

    if len(title) > 40:
        title = f'{title[:35]}…'.replace(' …', '…')

    if not disable_urls:
        if game[WEBSITES].get(country[ID]):
            title = '[{}]({})'.format(title, game[WEBSITES].get(country[ID]))

    new = (now - sale[START_DATE]).days < 1

    bold = '**' if new else ''
    emoji = NEW if new else ''

    time_left = sale[END_DATE] - now
    formatted_time = sale[END_DATE].strftime('%b %d')

    if time_left.days > 0:
        days = time_left.days

        if days < 2:
            emoji = EXP_TOMORROW
    else:
        hours = round(time_left.seconds / 60 / 60)

        if hours <= 24:
            emoji = EXP_TODAY

        if hours > 0:
            formatted_time = '{} ({}h)'.format(formatted_time, hours)
        else:
            minutes = round(time_left.seconds / 60)
            formatted_time = '{} ({}m)'.format(formatted_time, minutes)

    sale_price = format_float(sale[SALE_PRICE], country[DIGITS])
    full_price = format_float(price[FULL_PRICE], country[DIGITS])

    players = game[NUMBER_OF_PLAYERS]

    if players is None or players == 0:
        players = 'n/a'
    elif players == 1:
        players = '1'
    elif players == 2:
        players = '2'
    else:
        players = '1-{}'.format(players)

    metascore = game.get(SCORES, {}).get(METASCORE)
    if not metascore:
        metascore = '-'

    userscore = game.get(SCORES, {}).get(USERSCORE)
    if not userscore:
        userscore = '-'

    return f'{bold}{title}{bold}|{emoji}|{formatted_time}|' \
           f'{sale_price} {country[CURRENCY]} ~~{full_price}~~|{sale[DISCOUNT]}%|' \
           f'{players}|{metascore}|{userscore}'


def generate_country_tables(games, prices, system, country, disable_urls=False):
    now = datetime.utcnow()

    header = [
        'Title | - | Expiration | Price | % | Players | MS | US',
        '--- | :---: | --- | --- | :---: | :---: | :---: | :---: '
    ]

    new_sales = []
    week_sales = []
    current_sales = []

    games_on_sale = 0

    for game in games:
        if game[SYSTEM] != system:
            continue

        nsuid = game.get(NSUIDS, {}).get(country[REGION])

        if not nsuid:
            continue

        price = prices.get(nsuid, {}).get(country[ID])
        latest_sale = get_latest_sale(price)

        if not latest_sale:
            continue

        row = make_row(game, country, price, latest_sale, disable_urls=disable_urls)
        days = (now - latest_sale[START_DATE]).days

        if days < 1:
            new_sales.append(row)
        elif now.strftime("%V") == latest_sale[START_DATE].strftime("%V"):
            week_sales.append(row)
        else:
            current_sales.append(row)

        games_on_sale += 1

    return header + new_sales + week_sales, header + current_sales, games_on_sale


def generate_country_post(games, prices, system, country):
    country = COUNTRIES[country]

    week_sales, current_sales, games_on_sale = generate_country_tables(games, prices, system, country)

    if len(week_sales) + len(current_sales) > 35000:
        week_sales, current_sales, games_on_sale = \
            generate_country_tables(games, prices, system, country, disable_urls=True)

    title = f'[{country[FLAG]} {country[ID]}] Current Nintendo {system} eShop deals'

    content = [
        f'#{country[FLAG]} {country[NAME]} ({games_on_sale} deals)\n'
    ]

    content.extend(generate_header())

    if len(week_sales) > 2:
        content.append(f'##Deals of this week: {len(week_sales) - 2} deals\n')
        content.extend(week_sales)
    else:
        content.append('##No new deals :(')

    content.append(SEPARATOR)
    content.append(f'##Active deals: {len(current_sales) - 2} deals\n')
    content.extend(current_sales)
    content.extend(generate_footer())

    return title, '\n'.join(content)


def generate_main_post(games, prices, submissions, system):
    title = f'Current Nintendo {system} eShop deals'

    content = [
        '###Deals by country/region'
    ]

    for country, details in COUNTRIES.items():
        key = f'{system}/{country}'

        submission = submissions.get(key)

        if not submission:
            continue

        content.append(f'* [**{details[FLAG]} {details[NAME]}**]({submission[URL]})')

    content.extend(generate_footer())

    return title, '\n'.join(content)

