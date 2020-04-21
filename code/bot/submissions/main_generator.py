from bot.submissions.common import SEPARATOR
from bot.submissions.common import footer
from bot.submissions.common import header

from commons.config import USER_SUBREDDIT
from commons.config import COUNTRIES
from commons.emoji import EMPTY
from commons.keys import FLAG
from commons.keys import NAME
from commons.keys import REGION
from commons.settings import WEBSITE_URL


def make_row(game, countries_with_sale, avg_discount):
    countries = []

    for country in COUNTRIES:
        countries.append(countries_with_sale.get(country, EMPTY))

    countries = ''.join(countries)

    title = game.title

    if len(title) > 27:
        title = f'{title[:26]}…'.replace(' …', '…')

    return f'{title} | {countries} | {int(avg_discount)}%'
    # |{game.scores.metascore}|{game.scores.userscore}|{game.wishlisted}'


def make_table(games, prices, system):
    games = sorted(games.values(), key=lambda x: x.wishlisted, reverse=True)

    content = [
        f'Title | Regions | % ',  # | MS | US | {STAR} ',
        '--- | --- | :---: ',  # | :---: | :---: | :---:'
    ]

    for game in sorted(games[:50], key=lambda g: g.title.lower()):
        if game.system != system:
            continue

        if not game.wishlisted:
            continue

        countries = {}

        discounts = set()

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

            countries[country] = details[FLAG]

            discounts.add(latest_sale.discount)

        if len(countries):
            row = make_row(game, countries, sum(discounts) / len(discounts))
            content.append(row)

    if len(content) < 3:
        return None

    return '\n'.join(content)


def generate(games, prices, submissions, system):
    title = f'Current Nintendo {system} eShop deals'

    table = make_table(games, prices, system)

    content = []
    content.extend(header())

    content.append('')
    content.append('⬇ Regional posts with prices, dates, scores, and more.')
    content.append('')
    content.append('-|new sales this week|total sales')
    content.append('---|:---:|:---:')

    for country, details in COUNTRIES.items():
        key = f'{system}/{country}'

        submission = submissions.get(key)

        if not submission:
            continue

        full_url = f'https://www.reddit.com/r/{USER_SUBREDDIT}/comments/{submission.submission_id}'

        content.append(
            f'[{details[FLAG]} {details[NAME]}]({full_url})|{submission.new_sales}|{submission.total_sales}'
        )

    content.append('')

    if table:
        content.append(f'###Most [wishlisted]({WEBSITE_URL}) games on sale')
        content.append('')
        content.append(table)
        content.append(SEPARATOR)

    content.extend(footer())

    return title, '\n'.join(content)
