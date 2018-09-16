# Standard
import logging
from datetime import datetime

# Modules
from bot.db.mongo import PricesDatabase
from bot.commons.util import *

# Constants
from bot.commons.config import *
from bot.commons.keys import *
from bot.commons.util import *


LOG = logging.getLogger('📝')


PRICES_DB = PricesDatabase.instance()


def make_comment(games, country, country_details, disable_fulltitles=False, disable_urls=False, disable_fullprice=False, disable_decimals=False):
    now = datetime.utcnow().replace(tzinfo=None)

    text = []
    text.append('')

    text.append('Title | - | Expiration | Price | % | Players | MS | US')
    text.append('--- | :---: | --- | --- | :---: | :---: | :---: | :---: ')

    deal_count = 0

    for game in games:
        if country not in game[prices_]:
            continue

        title = game[final_title_]
        price = game[prices_][country]
        sale = price[sales_][-1]

        if sale[discount_] < 1:
            continue

        if not (sale[start_date_] < now < sale[end_date_]):
            continue

#        if disable_fulltitles:
        if len(title) > 30:
            title = title[:27] + '…'

        # Making titles as url if possible
        if not disable_urls:
            if country in game[websites_]:
                title = '[{}]({})'.format(
                    title,
                    game[websites_][country].replace('https://www.' if country != JP_ else 'https://', '//')
                )

        discount = sale[discount_]
        currency = country_details[currency_]

        sale_price = format_float(sale[sale_price_], country_details[digits_])
        full_price = format_float(price[full_price_], 0)

        if disable_decimals:
            sale_price = sale_price[:-2]
            full_price = full_price[:-2]

        time_left = sale[end_date_] - now
        time_format = '{}'.format(sale[end_date_].strftime('%b %d'))

        # Formating remaining time
        if time_left.days > 0:
            days = time_left.days

            warning = EMOJI_EXP_TOMORROW if days < 2 else ''
        else:
            hours = round(time_left.seconds / 60 / 60)
            warning = EMOJI_EXP_TODAY if hours <= 24 else ''

            if hours > 0:
                time_format = '{} ({}h)'.format(time_format, hours)
            else:
                minutes = round(time_left.seconds / 60)
                time_format = '{} ({}m)'.format(time_format, minutes)

        new = EMOJI_NEW if (now - sale[start_date_]).days < 1 else ''

        players = game[number_of_players_]

        # Formatting number of players
        if players is None or players == 0:
            players = 'n/a'
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
                ms = int(game[scores_][metascore_]) if game[scores_][metascore_] != '-' else game[scores_][metascore_]

            if userscore_ in game[scores_] and game[scores_][userscore_] is not None:
                us = '%.1f' % game[scores_][userscore_] if game[scores_][userscore_] != '-' else game[scores_][userscore_]

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
    text.insert(0, '> MS: Metascore | US: Userscore (both from metacritic.com)')
    text.insert(0, '')
    text.insert(0, '`{} new deal` `{} expires in 48hs` `{} expires in 24hs` `{} published by nintendo`'.format(
        EMOJI_NEW,
        EMOJI_EXP_TOMORROW,
        EMOJI_EXP_TODAY,
        EMOJI_NINTENDO
    ))

    return '\n'.join(text)


def make_post(games, countries, filtered=False):
    now = datetime.utcnow().replace(tzinfo=None)

    text = []

    # Building table header
    columns = 'Title'
    separator = '---'

    for country, country_details in countries:
        columns += ' | {}{}'.format(country_details[flag_], country)
        separator += ' | ---'

    if not filtered:
        text.append('')
        text.append('`{} new deal` `{} expires in 48hs` `{} expires in 24hs` `{} published by nintendo`'.format(
            EMOJI_NEW,
            EMOJI_EXP_TOMORROW,
            EMOJI_EXP_TODAY,
            EMOJI_NINTENDO
        ))
        text.append('')
        text.append('___')
        text.append('')
        text.append('# Relevant deals')
    else:
        text.append('')
        text.append('___')
        text.append('')
        text.append('# Games often on sale')
        text.append('')

    text.append('')
    text.append(columns)
    text.append(separator)

    for game in games:
        # Game title is EN or JP
        title = game[final_title_]  # + ' ' + str(game[relevance_])

        row = ''
        has_new_discount = False

        # Building discount table
        for country, country_details in countries:

            if country not in game[prices_]:
                row += '| '
                continue

            LOG.info('Adding {} discount for {}'.format(title, country))

            current_sale = game[prices_][country][sales_][-1]
            discount = current_sale[discount_]

            if discount < 1:
                row += '| '
                continue

            if not (current_sale[start_date_] < now < current_sale[end_date_]):
                row += '| '
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

        text.append(row)

    return '\n'.join(text)
