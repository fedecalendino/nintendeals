import logging
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from slugify import slugify_filename

from commons.classes import Score

slugify_filename.set_safe_chars('!-')

HEADERS = {'User-Agent': 'Mozilla/5.0'}
METACRITIC_URL = 'http://www.metacritic.com/game/{system}/{title}'

LOG = logging.getLogger('metacritic')


def normalize(string):
    string = string.replace('.', '')\
        .replace('®', '')\
        .replace('™', '')\
        .replace('/', '')\
        .replace('+', 'replacewithplus')

    string = slugify_filename(string, to_lower=True)\
        .replace('_', '-')\
        .replace('replacewithplus', '+')

    if string.endswith('+'):
        string = string[:-1] + '-+'

    return string


def extract_score(soup, tag, properties, cast=float):
    result = soup.find(tag, properties)

    try:
        return cast(result.contents[0])
    except:
        return None


def _get_scores(system, title):
    slug = normalize(title)

    url = METACRITIC_URL.format(system=system.lower(), title=slug)
    LOG.info('Fetching scores for {} on {}: {}'.format(title, system, url))

    request = Request(url, headers=HEADERS)
    content = urlopen(request).read()

    soup = BeautifulSoup(content, "html.parser")

    score = Score(days=14)

    score.metascore = extract_score(soup, 'span', {'itemprop': 'ratingValue'}, cast=int)
    score.userscore = extract_score(soup, 'div', {'class': lambda value: value and value.startswith('metascore_w user')})

    return score


PREFIXES = [
    '',

    ' for Nintendo Switch',

    ' - Digital Version',
    ' Digital Edition',

    ' - Nintendo Switch Edition',
    ': Nintendo Switch Edition',
    ' Nintendo Switch Edition',

    ': Complete Edition',
    ' Complete Edition',

    ' - Definitive Edition',

    ': Deluxe Edition',
    'Deluxe Edition',

    ': Special Edition',
    ' - Special Edition',
    ' Special Edition',

    ': Ultimate Edition',
    ' Ultimate Edition',
]


def get_scores(system, titles):
    system = system.lower()

    for title in titles:
        for prefix in PREFIXES:
            if prefix not in title:
                continue

            tmp = title.replace(prefix, '')

            try:
                score = _get_scores(system, tmp)

                if score.score != Score.NO_SCORE:
                    LOG.info(f'Score for {title}: {score.score}')
                    return score
            except Exception as e:
                LOG.debug(f'Error fetch score for {tmp}: {str(e)}')

    LOG.info(f'Score for {title}: {Score.NO_SCORE}')
    return Score(days=7)
