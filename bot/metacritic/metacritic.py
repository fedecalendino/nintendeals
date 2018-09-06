# Standard
import logging

# Dependencies
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from slugify import slugify_filename

METACRITIC_URL = 'http://www.metacritic.com/game/{system}/{title}'

LOG = logging.getLogger('💯')


def normalize(string):
    slugify_filename.set_safe_chars('!-')

    string = string.replace('.', '')
    string = string.replace('™', '')
    string = string.replace('/', '')
    string = slugify_filename(string, to_lower=True)
    string = string.replace('_', '-')

    return string


def extract_number(soup, tag, properties):
    result = soup.find(tag, properties)

    try:
        return float(result.contents[0])
    except:
        return None


def get_score(base_system, title):
    systems = [base_system.lower(), 'pc', 'playstation-4', 'xbox-one', 'ios']

    slug = normalize(title)

    metascore = None
    userscore = None

    score_system = None

    for system in systems:
        try:
            url = METACRITIC_URL.format(system=system, title=slug)

            LOG.error('Fetching scores for {} on {}: {}'.format(title, system, url))

            request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            content = urlopen(request).read()

            soup = BeautifulSoup(content, "html.parser")

            metascore = extract_number(soup, 'span', {'itemprop': 'ratingValue'})
            userscore = extract_number(soup, 'div', {'class': lambda value: value and value.startswith('metascore_w user')})

            if metascore is not None or userscore is not None:
                score_system = system
                break

        except Exception as e:
            pass

    if score_system is not None:
        if metascore is None:
            metascore = '-'
        if userscore is None:
            userscore = '-'
    
    return metascore, userscore, score_system
