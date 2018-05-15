# Standard
import re
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Dependencies
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# Statics
from app.commons.keys import *

METACRITIC_URL = 'http://www.metacritic.com/game/{system}/{title}'

LOG = logging.getLogger('metacritic')


def normalize(string):
    string = string.lower()
    string = re.sub(r'[\']', '', string)
    string = re.sub(r'[^a-zA-Z0-9\\+!]', '-', string)
    string = re.sub(r'-+', '-', string)
    string = re.sub(r'-$', '', string)

    return string


def extract_number(soup, tag, properties):
    result = soup.find(tag, properties)

    try:
        return float(result.contents[0])
    except:
        return None


def get_score(system, title):
    url = METACRITIC_URL.format(system=system.lower(), title=normalize(title))

    metascore = None
    userscore = None

    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, "html.parser")

        metascore = extract_number(soup, 'span', {'itemprop': 'ratingValue'})
        userscore = extract_number(soup, 'div', {'class': lambda value: value and value.startswith('metascore_w user')})
    except Exception as e:
        LOG.error("Fetching scores for {} on {}: {} ({})".format(title, system, e, url))
        pass

    if system != 'pc' and metascore is None and userscore is None:
        return get_score('pc', title)

    return metascore, userscore


def find_scores(game):
    if scores_ not in game:
        game[scores_] = {}

    if last_update_ not in game[scores_] or game[scores_][last_update_] + relativedelta(days=+14) < datetime.now():
        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        metascore, userscore = get_score(game[system_], title)

        game[scores_][last_update_] = datetime.now()

        if metascore is not None or userscore is not None:
            game[scores_][metascore_] = metascore
            game[scores_][userscore_] = userscore

    return game
