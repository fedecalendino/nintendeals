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


def filter_games(games, countries):
    now = datetime.utcnow().replace(tzinfo=None)

    new_deals = []
    old_deals = []
    regular_deals = []

    for game in games:
        if game[relevance_] <= 0:
            regular_deals.append(game)
            continue

        has_discount = False
        has_new_discount = False

        # Building discount table
        for country in countries:
            if country not in game[prices_]:
                continue

            sale = game[prices_][country][sales_][-1]
            discount = sale[discount_]

            if discount < 1:
                continue

            if not (sale[start_date_] < now < sale[end_date_]):
                continue

            has_discount = True

            if (now - sale[start_date_]).days < 1:
                has_new_discount = True

        if has_discount:
            if has_new_discount:
                new_deals.append(game)
            else:
                old_deals.append(game)

    return new_deals, old_deals, regular_deals


def build_reduced_table(games, countries, bold_titles=False, with_new_emoji=False):
    now = datetime.utcnow().replace(tzinfo=None)

    columns = 'Title'
    separator = '---'

    for country in countries:
        country_details = COUNTRIES[country]

        columns += '|{} {}'.format(country_details[flag_], country)
        separator += '|---:'

    table = [columns, separator]

    for game in games:
        title = game[final_title_]

        if bold_titles:
            if title.startswith(' '):
                row = ' **{}**'.format(title[1:])
            else:
                row = '**{}**'.format(title)
        else:
            row = title

        # Building discount table
        for country in countries:
            country_details = COUNTRIES[country]

            if country not in game[prices_]:
                row += '| '
                continue

            price = game[prices_][country]
            sale = game[prices_][country][sales_][-1]

            if sale[discount_] < 1:
                row += '| '
                continue

            if not (sale[start_date_] < now < sale[end_date_]):
                row += '| '
                continue

            time_left = sale[end_date_] - now

            # Formating remaining time
            if time_left.days > 0:
                warning = EMOJI_EXP_TOMORROW if time_left.days < 2 else ''
            else:
                hours = round(time_left.seconds / 60 / 60)
                warning = EMOJI_EXP_TODAY if hours <= 24 else ''

            currency = country_details[currency_]
            sale_price = format_float(sale[sale_price_], 0)
            full_price = format_float(price[full_price_], 0)

            LOG.info('Adding {} discount for {}'.format(title, country))

            row += '|{format}{currency}{sale_price}{format} ~~{currency}{full_price}~~'.format(
                format='**' if (now - sale[start_date_]).days < 1 else '',
                warning=warning,
                currency=currency,
                sale_price=sale_price,
                full_price=full_price
            )

        table.append(row)

    return table


def build_complete_table(games, country, urls=True, fullprice=True, decimals=True):
    now = datetime.utcnow().replace(tzinfo=None)

    country_details = COUNTRIES[country]

    table = [
        'Title | - | Expiration | Price | % | Players | MS | US',
        '--- | :---: | --- | --- | :---: | :---: | :---: | :---: '
    ]

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

        if len(title) > 26:
            title = title[:24] + '…'

        # Making titles as url if possible
        if urls:
            if country in game[websites_]:
                title = '[{}]({})'.format(
                    title,
                    game[websites_][country].replace('www.', '')
                )

        discount = sale[discount_]
        currency = country_details[currency_]

        sale_price = format_float(sale[sale_price_], country_details[digits_])
        full_price = format_float(price[full_price_], 0)

        if not decimals:
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

        new = (now - sale[start_date_]).days < 1

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
                us = '%.1f' % game[scores_][userscore_] if game[scores_][userscore_] != '-' else game[scores_][
                    userscore_]

        if new:
            if title.startswith(' '):
                title = ' **{}**'.format(title[1:])
            else:
                title = '**{}**'.format(title)

        if fullprice:
            price_format = '{currency}{sale_price} ~~{full_price}~~'.format(
                currency=currency, sale_price=sale_price, full_price=full_price)
        else:
            price_format = '{currency}{sale_price}'.format(
                currency=currency, sale_price=sale_price)

        # Creating row
        table.append(
            '{title}|{new}{warning}|*{time_left}*|{price}|`%{discount}`|{players}|{metascore}|{userscore}'.format(
                title=title, new=EMOJI_NEW if new else '', warning=warning, time_left=time_format,
                currency=currency, price=price_format, discount=discount, players=players,
                metascore=ms, userscore=us)
        )

    return table


def make_comment(games, country):
    country_details = COUNTRIES[country]

    new_deals, old_deals, regular_deals = filter_games(games, [country])

    games = []
    games.extend(new_deals)
    games.extend(old_deals)

    table = build_complete_table(games, country)

    if len('\n'.join(table)) > 9500:
        table = build_complete_table(games, country, fullprice=False)

        if len('\n'.join(table)) > 9500:
            table = build_complete_table(games, country, urls=False, fullprice=False)

    content = [
        '`{} new deal` `{} expires in 48hs` `{} expires in 24hs`'.format(EMOJI_NEW, EMOJI_EXP_TOMORROW, EMOJI_EXP_TODAY),
        '',
        '> MS: Metascore | US: Userscore (both from metacritic.com)',
        '___',
        '',
        '##{} {} ({} deals)'.format(country_details[flag_], country_details[name_], len(table) - 2),
        ''
    ]

    content.extend(table)

    if country_details[currency_] == COUNTRIES[US_][currency_]:
        content.append('___')
        content.append('> prices in **{}**'.format(country_details[currency_code_]))

    return '\n'.join(content)


def build_country_comments(games, countries):
    country_comments = {}

    for country in countries:
        country_details = COUNTRIES[country]

        LOG.info('Building reddit comment for {} {}'.format(country_details[flag_], country))

        country_comments[country] = make_comment(games, country)

    return country_comments


def build_reduced_footer(with_new=False, with_warnings=False):
    legend = ''

    if False:  # with_new:
        legend += '{} new deal - '.format(EMOJI_NEW)

    if False:  # with_warnings:
        legend += '{} expires in 48hs - {} expires in 24hs'.format(EMOJI_EXP_TOMORROW, EMOJI_EXP_TODAY)

    footer = []

    if len(legend) > 0:
        footer.append('> legend: {}'.format(legend))
        footer.append('')

    footer.append('> Prices in each country\'s currency')
    footer.append('')

    return footer


def make_post(games, countries):
    new_deals, old_deals, regular_deals = filter_games(games, countries)

    content = []

    if len(new_deals):
        table = build_reduced_table(new_deals, countries, bold_titles=True)

        total = len(table) - 2

        content.append('#New Sales {} ({} deal{})'.format(EMOJI_NEW, total, 's' if total > 1 else ''))
        content.extend(table)
        content.extend(build_reduced_footer())
    else:
        content.append('#No new sales today :(')

    content.append('___')

    if len(old_deals):
        table = build_reduced_table(old_deals, countries)

        total = len(table) - 2

        content.append('#Games on sale ({} deal{})'.format(total, 's' if total > 1 else ''))
        content.extend(table)
        content.extend(build_reduced_footer(with_warnings=True))

        content.append('___')

    if len(regular_deals):
        table = build_reduced_table(regular_deals, countries, with_new_emoji=True)

        total = len(table) - 2

        content.append('#Games often on sale ({} deal{})'.format(total, 's' if total > 1 else ''))
        content.extend(table)
        content.extend(build_reduced_footer(with_new=True, with_warnings=True))

    return '\n'.join(content)
