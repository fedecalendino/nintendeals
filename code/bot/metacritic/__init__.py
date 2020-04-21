import logging
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from slugify import slugify_filename

from commons.classes import Score

slugify_filename.set_safe_chars('!-')

HEADERS = {'User-Agent': 'Mozilla/5.0'}
METACRITIC_URL = 'http://www.metacritic.com/game/{system}/{title}'

LOG = logging.getLogger('metacritic')


CUSTOM_FIXES = {
    'Banner Saga 2': 'the-banner-saga-2',
    'Banner Saga Trilogy': 'the-banner-saga-trilogy',
    'Ittle Dew 2+': 'ittle-dew-2+',
    'Minecraft': 'minecraft-switch-edition',
    'N++ (NPLUSPLUS)': 'n++',
    'PICROSS S2': 'picross-s-2',
    'Velocity®2X': 'velocity-2X',

}


def normalize(string):

    if string in CUSTOM_FIXES:
        return CUSTOM_FIXES[string]

    string = string.replace('.', '')\
        .replace('®', '')\
        .replace('™', '') \
        .replace('*', '') \
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
        return cast(result.text)
    except:
        return None


def _get_scores(system, title):
    slug = normalize(title)

    url = METACRITIC_URL.format(system=system.lower(), title=slug)
    LOG.info(f'Fetching scores for {title} on {system}: {url}')

    request = Request(url, headers=HEADERS)
    content = urlopen(request).read()

    soup = BeautifulSoup(content, "html.parser")

    score = Score(days=14)

    score.metascore = extract_score(
        soup,
        'div',
        {'class': lambda value: value and value.startswith('metascore_w xlarge game')},
        cast=int
    )

    score.userscore = extract_score(
        soup,
        'div',
        {'class': lambda value: value and value.startswith('metascore_w user large game')}
    )

    return score


PREFIXES = [
    '',

    ' for Nintendo Switch',

    ' - Digital Version',
    ' Digital Edition',

    ' - Nintendo Switch Edition',
    ': Nintendo Switch Edition',
    ' Nintendo Switch Edition',
    ': Nintendo Switch Edition - Digital Version',

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

    ' -',
    '!',
]


def get_scores(system, titles):
    system = system.lower()

    for title in titles:
        if not title:
            continue

        for prefix in PREFIXES:
            if prefix not in title:
                continue

            tmp = title.replace(prefix, '')

            try:
                score = _get_scores(system, tmp)
                LOG.info(f'Score for {title}: {score}')
                return score
            except Exception as e:
                LOG.info(f'Error fetch score for {tmp}: {str(e)}')

        LOG.info(f'Score for {title}: {Score.NO_SCORE}')

    return Score(days=7)
