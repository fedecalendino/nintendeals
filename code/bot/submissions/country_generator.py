from datetime import datetime

from bot.submissions.common import SEPARATOR
from bot.submissions.common import footer
from bot.submissions.common import header
from commons.config import COUNTRIES
from commons.emoji import ALL_TIME_LOW
from commons.emoji import EXP_TODAY
from commons.emoji import EXP_TOMORROW
from commons.emoji import FIRST_TIME
from commons.emoji import GEM
from commons.emoji import NEW
from commons.emoji import NINTENDO
from commons.emoji import PLAYERS
from commons.emoji import STAR
from commons.emoji import WARNING
from commons.keys import CURRENCY_CODE
from commons.keys import DIGITS
from commons.keys import FLAG
from commons.keys import ID
from commons.keys import NAME
from commons.keys import REGION
from commons.util import format_float


def make_row(game, country, price, sale, disable_url=False, **kwargs):
    now = datetime.utcnow()

    title = game.titles.get(country[REGION], game.title)
    country_price = price.prices[country[ID]]

    if game.published_by_nintendo:
        title = f'{NINTENDO} {title}'

    if game.hidden_gem:
        title = f'{GEM} {title}'

    if len(title) > 23:
        title = f'{title[:23]}…'.replace(' …', '…')

    if not disable_url:
        if game.websites.get(country[ID]):
            title = '[{}]({})'.format(title, game.websites.get(country[ID]))

    new = (now - sale.start_date).days < 1

    if not kwargs.get('disable_title_formatting', False):
        bold = '**' if new else ''
    else:
        bold = ''

    emoji = ''

    if new:
        emoji += NEW

    if len(country_price.sales) == 1:
        emoji += FIRST_TIME
    elif min([sale.sale_price for sale in country_price.sales]) == sale.sale_price:
        emoji += ALL_TIME_LOW

    time_left = sale.end_date - now
    formatted_time = sale.end_date.strftime('%b %d')

    if time_left.days > 0:
        days = time_left.days

        if days < 2:
            emoji += EXP_TOMORROW
    else:
        hours = round(time_left.seconds / 60 / 60)

        if hours <= 24:
            emoji += EXP_TODAY

        if hours > 0:
            formatted_time = f'{formatted_time} ({hours}h)'
        else:
            minutes = round(time_left.seconds / 60)
            formatted_time = f'{formatted_time} ({minutes}m)'

    if not kwargs.get('disable_extra_zeros', False):
        digits = country[DIGITS]
    else:
        digits = 0

    sale_price = format_float(sale.sale_price, digits)
    full_price = format_float(country_price.full_price, digits)

    if not kwargs.get('disable_full_prices', False):
        full_price = f' ~~{full_price}~~'
    else:
        full_price = ''

    wishlisted = game.wishlisted if game.wishlisted else ''
    metascore = game.scores.metascore if game.scores.metascore != '-' else ''
    userscore = game.scores.userscore if game.scores.userscore != '-' else ''

    row = f'{bold}{title}{bold}|{emoji}|{formatted_time}|' \
          f'{sale_price}{full_price}'

    if not kwargs.get('disable_discount_formatting', False):
        row += f'|`{sale.discount}`'
    else:
        row += f'|{sale.discount}'

    if not kwargs.get('disable_players', False):
        row += f'|{game.players}'

    if not kwargs.get('disable_scores', False):
        row += f'|{metascore}|{userscore}'

    if not kwargs.get('disable_wishlisted', False):
        row += f'|{wishlisted}'

    return row


def make_tables(games, prices, system, country, **kwargs):
    now = datetime.utcnow()

    table_columns = 'Title '
    table_separators = '--- '

    table_columns += '| - '
    table_separators += '| --- '

    table_columns += '| Expiration '
    table_separators += '| --- '

    table_columns += f'| {country[CURRENCY_CODE]}s '
    table_separators += '| :---: '

    table_columns += f'| % '
    table_separators += '| :---: '

    if not kwargs.get('disable_players', False):
        table_columns += f'| {PLAYERS} '
        table_separators += '| :---: '

    if not kwargs.get('disable_scores', False):
        table_columns += '| MS | US '
        table_separators += '| :---: | :---: '

    if not kwargs.get('disable_wishlisted', False):
        table_columns += f'| {STAR}'
        table_separators += '| :---:'

    header = [table_columns, table_separators]

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

        days = (now - latest_sale.start_date).days

        if kwargs.get('disable_soon_to_expire', False):
            time_left = latest_sale.end_date - now

            if time_left.days < 2:
                continue

        row = make_row(
            game=game,
            country=country,
            price=price,
            sale=latest_sale,
            disable_url=kwargs.get('disable_new_urls', False),
            **kwargs
        )

        if days < 1:
            new_sales.append(row)
        elif now.strftime("%V") == latest_sale.start_date.strftime("%V"):
            week_sales.append(row)
        else:
            current_sales.append(row)

        games_on_sale += 1

    return header + new_sales + week_sales, header + current_sales, games_on_sale


def generate(games, prices, system, country):
    country = COUNTRIES[country]

    modifiers = {}

    for modifier in [
        'unused',
        'disable_title_formatting',
        'disable_current_urls',
        'disable_new_urls',
        'disable_full_prices',
        'disable_players',
        'disable_wishlisted',
        'disable_scores',
        'disable_soon_to_expire',
        'disable_discount_formatting',
        'disable_extra_zeros',
    ]:
        modifiers[modifier] = True

        week_sales, current_sales, total_sales = make_tables(games, prices, system, country, **modifiers)

        size = len(''.join(week_sales)) + len(''.join(current_sales))

        if size < 38000:
            break

    title = f'{country[FLAG]} {country[ID]} ▪️ Current Nintendo {system} eShop deals'

    content = [
        f'#{country[NAME]}: {total_sales} deals\n'
    ]

    content.extend(
        header(
            system=system,
            country=country[ID],
            disable_players=modifiers.get('disable_players', False),
            disable_wishlisted=modifiers.get('disable_wishlisted', False)
        )
    )

    if len(week_sales) > 2:
        content.append(f'##Deals of this week: {len(week_sales) - 2} deals\n')
        content.extend(week_sales)
    else:
        content.append('##No new deals :(')

    content.append(SEPARATOR)
    content.append(f'##Active deals: {len(current_sales) - 2} deals\n')
    content.extend(current_sales)

    content.append('')

    if any((
            modifiers.get('disable_current_urls', False),
            modifiers.get('disable_full_prices', False),
            modifiers.get('disable_players', False),
            modifiers.get('disable_scores', False),
    )):
        content.append(f'{WARNING} some information is missing to fit eveything into reddit\'s 40k character limit\n')

        content.append('')

        if modifiers.get('disable_current_urls', False):
            content.append('* urls')
        if modifiers.get('disable_full_prices', False):
            content.append('* full prices')
        if modifiers.get('disable_players', False):
            content.append('* number of players')
        if modifiers.get('disable_scores', False):
            content.append('* metacritic scores')

    content.append('')

    content.extend(footer(system, country[ID]))

    return title, '\n'.join(content), len(week_sales) - 2, total_sales
