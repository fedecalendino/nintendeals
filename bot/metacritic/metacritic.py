# Standard
import re
import logging

# Dependencies
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

METACRITIC_URL = 'http://www.metacritic.com/game/{system}/{title}'

LOG = logging.getLogger('metacritic')


def normalize(string):
    string = string.lower()
    string = string.replace('é', 'e')
    string = re.sub(r'[\'\.]', '', string)
    string = re.sub(r'[^a-zA-Z0-9\\+\-!]', '|', string)
    string = re.sub(r'\|+', '|', string)
    string = re.sub(r'\|$', '', string)

    string = re.sub(r'\|', '-', string)

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

    if metascore is None and userscore is None:
        if system != 'pc':
            return get_score('pc', title)

    return metascore, userscore
