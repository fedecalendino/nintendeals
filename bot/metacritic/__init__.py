import logging
from datetime import datetime
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from slugify import slugify_filename

from commons.keys import LAST_UPDATE
from commons.keys import METASCORE
from commons.keys import USERSCORE


slugify_filename.set_safe_chars('!-')

HEADERS = {'User-Agent': 'Mozilla/5.0'}
METACRITIC_URL = 'http://www.metacritic.com/game/{system}/{title}'

LOG = logging.getLogger('metacritic')


def normalize(string):
    string = string.replace('.', '')\
        .replace('™', '')\
        .replace('/', '')

    string = slugify_filename(string, to_lower=True)\
        .replace('_', '-')

    return string


def extract_score(soup, tag, properties, cast=float):
    result = soup.find(tag, properties)

    try:
        return str(cast(result.contents[0]))
    except:
        return None


def get_scores(system, title, scores=None):
    if not scores:
        scores = {
            METASCORE: None,
            USERSCORE: None,
            LAST_UPDATE: None
        }

    now = datetime.now()

    system = system.lower()
    slug = normalize(title)

    metascore = scores.get(METASCORE)
    userscore = scores.get(USERSCORE)
    last_update = scores.get(LAST_UPDATE)

    days = 28 if metascore in [None, '-'] else 14

    if not last_update or last_update + relativedelta(days=+days) < now:
        try:
            url = METACRITIC_URL.format(system=system.lower(), title=slug)
            LOG.info('Fetching scores for {} on {}: {}'.format(title, system, url))

            request = Request(url, headers=HEADERS)
            content = urlopen(request).read()

            soup = BeautifulSoup(content, "html.parser")

            metascore = extract_score(soup, 'span', {'itemprop': 'ratingValue'}, cast=int)
            userscore = extract_score(soup, 'div', {'class': lambda value: value and value.startswith('metascore_w user')})
        except:
            pass

    scores[METASCORE] = metascore if metascore else '-'
    scores[USERSCORE] = userscore if userscore else '-'

    scores[LAST_UPDATE] = now

    return scores
