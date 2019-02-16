import operator
from datetime import datetime

from commons.config import COUNTRIES

from commons.emoji import EXP_TODAY
from commons.emoji import EXP_TOMORROW
from commons.emoji import NEW
from commons.emoji import NINTENDO
from commons.emoji import STAR

from commons.keys import CURRENCY
from commons.keys import CURRENCY_CODE
from commons.keys import DIGITS
from commons.keys import FLAG
from commons.keys import ID
from commons.keys import NAME
from commons.keys import REGION

from commons.settings import WEBSITE_URL

from commons.util import format_float


SEPARATOR = '\n___\n'


def generate_header(system=None, country=None):

    header = []

    if system:
        header.append(f'>`{NEW} new` ')
        header.append(f'`{EXP_TOMORROW} expires tomorrow` ')
        header.append(f'`{EXP_TODAY} expires today` ')

    header.append(f'`{STAR} wishlist count` ')
    header.append(f'`{NINTENDO} published by nintendo`')
    header.append(SEPARATOR)

    if system:
        header.append(f'You can add games to your wishlist [HERE]({WEBSITE_URL}/wishlist/{system.lower()}/{country.lower()})')

    return header


def generate_footer(system=None, country=None):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    footer = [
        SEPARATOR,
        '* Developed by /u/uglyasablasphemy | [Switch Friend Code](https://nin.codes/uglyasablasphemy)',
        '* Use [RES](https://redditenhancementsuite.com) for table sorting and more',
        '* If you have perfomance issues, you might want to check out:',
        '   * [Reddit is Fun](https://play.google.com/store/apps/details?id=com.andrewshu.android.reddit)',
        '   * [Apollo for Reddit](https://itunes.apple.com/us/app/apollo-for-reddit/id979274575)',
        SEPARATOR,
        f'Last update: {timestamp}'
    ]

    if system:
        footer.append(SEPARATOR)
        footer.append(f'You can add games to your wishlist [HERE]({WEBSITE_URL}/wishlist/{system.lower()}/{country.lower()})')

    return footer


def make_countries_row(game, country, price, sale, disable_urls=False):
    now = datetime.utcnow()

    title = game.titles.get(country[REGION], game.title)
    title = title[1:] if title.startswith(' ') else title

    if len(title) > 40:
        title = f'{title[:35]}…'.replace(' …', '…')

    if not disable_urls:
        if game.websites.get(country[ID]):
            title = '[{}]({})'.format(title, game.websites.get(country[ID]))

    new = (now - sale.start_date).days < 1

    bold = '**' if new else ''
    emoji = NEW if new else ''

    time_left = sale.end_date - now
    formatted_time = sale.end_date.strftime('%b %d')

    if time_left.days > 0:
        days = time_left.days

        if days < 2:
            emoji = EXP_TOMORROW
    else:
        hours = round(time_left.seconds / 60 / 60)

        if hours <= 24:
            emoji = EXP_TODAY

        if hours > 0:
            formatted_time = f'{formatted_time} ({hours}h)'
        else:
            minutes = round(time_left.seconds / 60)
            formatted_time = f'{formatted_time} ({minutes}m)'

    country_price = price.prices[country[ID]]
    sale_price = format_float(sale.sale_price, country[DIGITS])
    full_price = format_float(country_price.full_price, country[DIGITS])

    return f'{bold}{title}{bold}|{emoji}|{formatted_time}|' \
           f'{sale_price} ~~{full_price}~~|`{sale.discount}%`|' \
           f'{game.players}|{game.scores.score}|' \
           f'{game.wishlisted if game.wishlisted else "-"}'


def generate_country_tables(games, prices, system, country, disable_urls=False):
    now = datetime.utcnow()

    header = [
        f'Title | - | Expiration | {country[CURRENCY]} ({country[CURRENCY_CODE]}) | % | Players | Score | {STAR}',
        '--- | :---: | --- | :---: | :---: | :---: | :---: | :---:'
    ]

    new_sales = []
    week_sales = []
    current_sales = []

    games_on_sale = 0

    for game_id, game in games.items():
        if game.system != system:
            continue

        nsuid = game.nsuids.get(country[REGION])

        if not nsuid:
            continue

        price = prices.get(nsuid)

        if not price:
            continue

        country_price = price.prices[country[ID]]

        if not country_price:
            continue

        latest_sale = country_price.active

        if not latest_sale:
            continue

        row = make_countries_row(game, country, price, latest_sale, disable_urls=disable_urls)
        days = (now - latest_sale.start_date).days

        if days < 1:
            new_sales.append(row)
        elif now.strftime("%V") == latest_sale.start_date.strftime("%V"):
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

    title = f'{country[FLAG]} {country[ID]} ▪️ Current Nintendo {system} eShop deals'

    content = [
        f'#{country[NAME]}: {games_on_sale} deals\n'
    ]

    content.extend(generate_header(system, country[ID]))

    if len(week_sales) > 2:
        content.append(f'##Deals of this week: {len(week_sales) - 2} deals\n')
        content.extend(week_sales)
    else:
        content.append('##No new deals :(')

    content.append(SEPARATOR)
    content.append(f'##Active deals: {len(current_sales) - 2} deals\n')
    content.extend(current_sales)
    content.extend(generate_footer(system, country[ID]))

    return title, '\n'.join(content)


def make_main_row(game, countries):
    countries = ' '.join([f'`{country[FLAG]}{country[ID]}`' for country in countries])

    return f'{game.title}|{countries}|{game.scores.score}|{game.wishlisted}'


def generate_main_table(games, prices, system):
    games = sorted(games.values(), key=lambda x: x.wishlisted, reverse=True)

    content = [
        f'Title | On sale on | Score | {STAR} ',
        '--- | --- | :---: | :---:'
    ]

    for game in games:
        if game.system != system:
            continue

        countries = []

        for country, details in COUNTRIES.items():
            nsuid = game.nsuids.get(details[REGION])

            if not nsuid:
                continue

            price = prices.get(nsuid)

            if not price:
                continue

            country_price = price.prices[country]

            if not country_price:
                continue

            latest_sale = country_price.active

            if not latest_sale:
                continue

            if game.wishlisted < 25:
                continue

            countries.append(details)

        if len(countries):
            row = make_main_row(game, countries)
            content.append(row)

    if len(content) < 3:
        return None

    return '\n'.join(content)


def generate_main_post(games, prices, submissions, system):
    title = f'Current Nintendo {system} eShop deals'

    table = generate_main_table(games, prices, system)

    content = []

    content.extend(generate_header())

    if table:
        content.append('###Most wanted games on sale')
        content.append('')
        content.append(table)
        content.append(SEPARATOR)

    content.append('###Full deals by country/region')

    for country, details in COUNTRIES.items():
        key = f'{system}/{country}'

        submission = submissions.get(key)

        if not submission:
            continue

        content.append(f'* ##[**{details[FLAG]} {details[NAME]}**]({submission.url})')

    content.extend(generate_footer())

    return title, '\n'.join(content)
