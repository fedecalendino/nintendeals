# Standard
from datetime import datetime
import logging

# Modules
from app.commons.util import *

# Constants
from app.commons.config import *
from app.commons.keys import *

LOG = logging.getLogger('posts.generator')


def make_comment(games, country, country_details):
    now = datetime.utcnow().replace(tzinfo=None)

    text = []
    text.append('')

    text.append('Title | Expiration | Price | % | Players | Score')
    text.append('--- | --- | --- | --- | --- | ---')

    deal_count = 0

    for game in games:
        if country not in game[prices_]:
            continue

        details = game[prices_][country]

        if len(details) < 1:
            continue

        if title_ in game:
            title = game[title_]

            if len(title) > 35:
                title = title[:30] + '…'
        else:
            title = game[title_jp_]

            if len(title) > 30:
                title = title[:25] + '…'

        if country in game[websites_]:
            title = "[{}]({})".format(title, game[websites_][country])

        price = details[-1]

        currency = country_details[currency_]
        sale_price = format_float(price[sale_price_], country_details[digits_])
        full_price = format_float(price[full_price_], 0)
        discount = price[discount_]

        if price[end_date_] < now:
            continue

        time_left = price[end_date_] - now

        if time_left.days > 0:
            days = time_left.days
            time = "{}d".format(days)

            warning = EMOJI_EXP_TOMORROW if days < 2 else ''
        else:
            hours = round(time_left.seconds / 60 / 60)
            time = "{}h".format(hours)

            warning = EMOJI_EXP_TODAY if hours <= 24 else ''

            if hours <= 1:
                continue

        new = EMOJI_NEW if (now - price[start_date_]).days < 2 else ''

        players = game[number_of_players_]

        if players is None or players == 0:
            players = '- tbd -'
        elif players == 1:
            players = '1 player'
        elif players == 2:
            players = '1-2 players'
        else:
            players = 'up to {}'.format(players)

        score = ''

        if scores_ in game and len(game[scores_]) > 0:
            if metascore_ in game[scores_] and game[scores_][metascore_] is not None:
                score = "{} `{}`".format(EMOJI_METACRITIC, int(game[scores_][metascore_]))
            elif userscore_ in game[scores_] and game[scores_][userscore_] is not None:
                score = "{} `{}`".format(EMOJI_USER, "%.1f" % game[scores_][userscore_])

        text.append(
            '{title} {new}{warning} | '
            '*{end_date} ({time_left})* | '
            '**{currency}{sale_price}** ~~{full_price}~~ | '
            '`{discount}%`| '
            '{players} | {score}'.format(
                title=title, new=new, warning=warning,
                end_date=price[end_date_].strftime("%b %d"), time_left=time,
                currency=currency, sale_price=sale_price, full_price=full_price,
                discount=discount, players=players,
                score=score)
        )

        deal_count += 1

    text.insert(0, '')
    text.insert(0, '##{} {} ({} deals)'.format(country_details[flag_], country_details[name_], deal_count))
    text.insert(0, '')
    text.insert(0, '___')
    text.insert(0, '')
    text.insert(0, '`{} new` `{} expires in 48hs` `{} expires in 24hs` `{}️ metascore` `{} userscore`'.format(
        EMOJI_NEW, EMOJI_EXP_TOMORROW, EMOJI_EXP_TODAY, EMOJI_METACRITIC, EMOJI_USER))

    return '\n'.join(text)


def make_post(games, countries):
    now = datetime.utcnow().replace(tzinfo=None)

    text = []

    columns = 'Title'
    separator = '---'

    for country, country_details in countries:
        columns += ' | {} {}'.format(country_details[flag_], country)
        separator += ' | ---'

    text.append('')
    text.append('`{} new deal` `{} best deal` `{} expires in 48hs` `{} expires in 24hs`'.format(
        EMOJI_NEW, EMOJI_MAX_DISCOUNT, EMOJI_EXP_TOMORROW, EMOJI_EXP_TODAY))
    text.append('')
    text.append('___')
    text.append('')
    text.append(columns)
    text.append(separator)

    count = 0

    for game in games:
        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        LOG.info('Adding {} to post'.format(title))

        row = title

        for country, country_details in countries:
            LOG.info('Adding {} discount for {}'.format(title, country))

            if country in game[prices_] and len(game[prices_][country]) == 0:
                LOG.info('No {} discount for {}'.format(title, country))

                row += ' | '
                continue

            price = game[prices_][country][-1]

            if price[end_date_] is None:
                continue

            if price[end_date_] < now:
                LOG.info('No {} discount for {}'.format(title, country))

                row += ' | '
                continue

            discount = price[discount_]

            time_left = price[end_date_] - now

            if time_left.days > 0:
                days = time_left.days
                warning = EMOJI_EXP_TOMORROW if days < 2 else ''
            else:
                hours = round(time_left.seconds / 60 / 60)
                warning = EMOJI_EXP_TODAY if hours <= 24 else ''

            new = EMOJI_NEW if (now - price[start_date_]).days < 2 else ''

            best_discount = discount
            all_equals = True

            for _, prices in game[prices_].items():

                if len(prices) == 0:
                    continue

                if prices[-1][end_date_] is None:
                    continue

                if len(prices) > 0 and prices[-1][end_date_] > now:

                    if prices[-1][discount_] > best_discount:
                        best_discount = prices[-1][discount_]

                    if prices[-1][discount_] != best_discount:
                        all_equals = False

            if not all_equals and best_discount == discount:
                best_discount = EMOJI_MAX_DISCOUNT
            else:
                best_discount = ''

            row += '|`{discount}% {new}{best}{warning}`'.format(discount=discount, new=new, best=best_discount, warning=warning)

        text.append(row)
        count += 1

    return '\n'.join(text)
