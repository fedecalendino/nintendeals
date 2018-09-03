# Standard
import logging
from datetime import datetime

# Modules
from bot.db.mongo import PricesDatabase
from bot.commons.util import *

# Constants
from bot.commons.config import *
from bot.commons.keys import *


LOG = logging.getLogger('📝')


PRICES_DB = PricesDatabase.instance()


def make_comment(games, country, country_details, disable_urls=False, disable_fullprice=False, disable_decimals=False):
    now = datetime.utcnow().replace(tzinfo=None)

    text = []
    text.append('')

    text.append('Title | - | Expiration | Price | % | Players | MS | US')
    text.append('--- | :---: | --- | --- | :---: | :---: | :---: | :---: ')

    deal_count = 0

    for game in games:

        region = country_details[region_]

        if region not in game[ids_]:
            continue

        prices = PRICES_DB.load(game[ids_][region])

        if country not in prices[countries_] or prices[countries_][country] is None:
            continue

        if sales_ not in prices[countries_][country]:
            continue

        current_sale = prices[countries_][country][sales_][-1]

        if current_sale[end_date_] < now:
            continue

        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        if len(title) > 25:
            title = title[:23] + '…'

        # Making titles as url if possible
        if not disable_urls:
            if country in game[websites_]:
                title = '[{}]({})'.format(
                    title,
                    game[websites_][country].replace('https://www.', '//')
                )

        discount = current_sale[discount_]

        if discount < 1:
            continue

        currency = country_details[currency_]

        sale_price = format_float(current_sale[sale_price_], country_details[digits_])
        full_price = format_float(prices[countries_][country][full_price_], 0)

        if disable_decimals:
            sale_price = sale_price[:-2]
            full_price = full_price[:-2]

        time_left = current_sale[end_date_] - now
        time_format = '{}'.format(current_sale[end_date_].strftime('%b %d'))

        # Formating remaining time
        if time_left.days > 0:
            days = time_left.days

            warning = EMOJI_EXP_TOMORROW if days < 2 else ''
        else:
            hours = round(time_left.seconds / 60 / 60)
            time_format = '{} ({}h)'.format(time_format, hours)

            warning = EMOJI_EXP_TODAY if hours <= 24 else ''

            if hours == 0:
                minutes = round(time_left.seconds / 60)
                time_format = '{} ({}m)'.format(time_format, minutes)

        new = EMOJI_NEW if (now - current_sale[start_date_]).days < 1 else ''

        players = game[number_of_players_]

        # Formatting number of players
        if players is None or players == 0:
            players = 'tbd'
        elif players == 1:
            players = '1'
        elif players == 2:
            players = '2'
        else:
            players = '1-{}'.format(players)

        ms = ''
        us = ''

        # Formatting metacritic score
        if scores_ in game and len(game[scores_]) > 0:
            if metascore_ in game[scores_] and game[scores_][metascore_] is not None:
                ms = int(game[scores_][metascore_])

            if userscore_ in game[scores_] and game[scores_][userscore_] is not None:
                us = '%.1f' % game[scores_][userscore_]

        if new:
            title = '**{}**'.format(title)

        if disable_fullprice:
            price_format = '{currency}{sale_price}'.format(currency=currency, sale_price=sale_price)
        else:
            price_format = '{currency}{sale_price} ~~{full_price}~~'.format(currency=currency, sale_price=sale_price, full_price=full_price)

        # Creating row
        text.append(
            '{title}|{new}{warning}|*{time_left}*|{price}|`%{discount}`|{players}|{metascore}|{userscore}'.format(
                title=title, new=new, warning=warning, time_left=time_format,
                currency=currency, price=price_format, discount=discount, players=players,
                metascore=ms, userscore=us)
        )

        deal_count += 1

    if country_details[currency_] == COUNTRIES[US_][currency_]:
        text.append('___')
        text.append('> prices in **{}**'.format(country_details[currency_code_]))

    # Inserting comment headers
    text.insert(0, '')
    text.insert(0, '##{} {} ({} deals)'.format(country_details[flag_], country_details[name_], deal_count))
    text.insert(0, '')
    text.insert(0, '___')
    text.insert(0, '')
    text.insert(0, '`{} new` `{} expires in 48hs` `{} expires in 24hs`'.format(
        EMOJI_NEW, EMOJI_EXP_TOMORROW, EMOJI_EXP_TODAY))

    return '\n'.join(text)


def make_post(games, countries):
    now = datetime.utcnow().replace(tzinfo=None)

    text = []

    # Building table header
    columns = 'Title'
    separator = '---'

    for country, country_details in countries:
        columns += ' | {}{}'.format(country_details[flag_], country)
        separator += ' | ---'

    text.append('')
    text.append('`{} new deal` `{} expires in 48hs` `{} expires in 24hs`'.format(EMOJI_NEW, EMOJI_EXP_TOMORROW, EMOJI_EXP_TODAY))
    text.append('')
    text.append('___')
    text.append('')
    text.append(columns)
    text.append(separator)

    count = 0

    for game in games:
        has_discount = False

        # Game title is EN or JP
        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        # LOG.info('Adding {} to post'.format(title))

        row = ''
        has_new_discount = False

        # Building discount table
        for country, country_details in countries:
            region = country_details[region_]

            if region not in game[ids_]:
                row += ' | '
                continue

            prices = PRICES_DB.load(game[ids_][region])

            if country not in prices[countries_] or prices[countries_][country] is None:
                row += ' | '
                continue

            if sales_ not in prices[countries_][country]:
                row += ' | '
                continue

            current_sale = prices[countries_][country][sales_][-1]

            if current_sale[end_date_] < now:
                row += ' | '
                continue

            LOG.info('Adding {} discount for {}'.format(title, country))

            has_discount = True

            discount = current_sale[discount_]

            if discount < 1:
                continue

            time_left = current_sale[end_date_] - now

            if time_left.days > 0:
                days = time_left.days
                warning = EMOJI_EXP_TOMORROW if days < 2 else ''
            else:
                hours = round(time_left.seconds / 60 / 60)
                warning = EMOJI_EXP_TODAY if hours <= 24 else ''

            if (now - current_sale[start_date_]).days < 1:
                new = EMOJI_NEW
                has_new_discount = True
            else:
                new = ''

            row += '|`%{discount}{new}{warning}`'.format(discount=discount, new=new, warning=warning)

        if has_new_discount:
            row = "**{}**{}".format(title, row)
        else:
            row = "{}{}".format(title, row)

        if has_discount:
            text.append(row)
            count += 1

    return '\n'.join(text)


def make_wishlist_post(games):
    countries = ' '.join(COUNTRIES.keys())

    text = []
    text.append('')
    text.append('> To add game to your wishlist click on {}'.format(EMOJI_PLUS))
    text.append('')
    text.append('')
    text.append('Title | Actions')
    text.append('--- | :---: ')

    for game in games[:50]:
        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        text.append(
            '{}|{}'.format(
                title,
                '[{emoji}](http://www.reddit.com/message/compose?to={to}&subject=add: {game_id}&message={body})'.format(
                    emoji=EMOJI_PLUS, to=REDDIT_USERNAME, game_id=game[id_], body=countries),
            )
        )

    return '\n'.join(text)