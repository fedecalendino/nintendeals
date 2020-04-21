import logging
from datetime import datetime
from datetime import timedelta
from random import randint

from commons.config import COUNTRIES
from commons.config import REGIONS
from commons.emoji import GEM
from commons.emoji import NINTENDO
from commons.keys import EU
from commons.keys import NA
from commons.keys import WEBSITE
from commons.util import build_game_id


class Singleton(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)

        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)

        return cls._instance


class Game:

    def __init__(self, **data):
        self._id = build_game_id(data['_id'], data['system'])
        self.system = data['system']

        self.nsuids = data.get('nsuids', {region: None for region in REGIONS})
        self.titles = data.get('titles', {region: None for region in REGIONS})
        self.release_dates = data.get('release_dates', {region: None for region in REGIONS})

        self.wishlisted = data.get('wishlisted', 0)
        self.wishlisted_history = data.get('wishlisted_history', {})

        self.hidden_gem = data.get('hidden_gem', False)

        self.number_of_players = data.get('number_of_players', 0)
        self.published_by_nintendo = data.get('published_by_nintendo', False)
        self.categories = sorted(list(set(data.get('categories', []))))

        self.websites = data.get('websites', {country: None for country, dets in COUNTRIES.items() if WEBSITE in dets})
        self.scores = Score(**data.get('scores', {}))

        self.free_to_play = data.get('free_to_play', False)

        self._title = None

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        if self._title:
            return self._title

        self._title = [title for title in self.titles.values() if title][0]

        if self.published_by_nintendo:
            self._title = f' {NINTENDO} {self._title}'

        if self.hidden_gem:
            self._title = f' {GEM} {self._title}'

        return self._title

    @property
    def wishlisted_average(self):
        values = [value for value in self.wishlisted_history.values() if value > 0]
        return int(sum(values) / len(values)) if len(values) else 0

    @property
    def release_date(self):
        return [release_date for release_date in self.release_dates.values() if release_date][0]

    @property
    def title_en(self):
        return self.titles.get(NA, self.titles.get(EU))

    @property
    def players(self):
        if self.number_of_players in [None, 0]:
            return 'n/a'
        elif self.number_of_players in [1]:
            return '1'
        else:
            return f'{self.number_of_players}'

    def dump(self):
        tmp = self.__dict__.copy()
        tmp['title'] = self.title
        tmp['release_date'] = str(self.release_date)
        tmp['scores'] = self.scores.dump()

        return tmp

    def __repr__(self):
        return f'{self.id} > {self.title} ({self.system})'


class Score:

    NO_SCORE = '-'

    def __init__(self, **data):
        days = data.get('days', 0)

        if days:
            days += randint(1, days)

        self.metascore = data.get('metascore')

        if not self.metascore:
            self.metascore = self.NO_SCORE

        self.userscore = data.get('userscore')

        if not self.userscore:
            self.userscore = self.NO_SCORE

        self.next_update = data.get('next_update', datetime.utcnow() + timedelta(days=days))

    def dump(self):
        tmp = self.__dict__.copy()

        return tmp

    @property
    def score(self):
        scores = []

        if self.metascore not in [None, self.NO_SCORE]:
            scores.append(str(self.metascore))
        else:
            scores.append(self.NO_SCORE)
        
        if self.userscore not in [None, self.NO_SCORE]:
            scores.append(f'{self.userscore:.1f}')
        else:
            scores.append(self.NO_SCORE)

        return '/'.join(scores)

    def __repr__(self):
        return f'{self.metascore}/{self.userscore}'


class Sale:

    def __init__(self, **data):
        self.discount = data['discount']
        self.sale_price = data['sale_price']
        self.start_date = data['start_date']
        self.end_date = data['end_date']

    @property
    def active(self):
        return self.start_date < datetime.utcnow() < self.end_date

    def dump(self):
        tmp = self.__dict__.copy()

        return tmp


class CountryPrice:

    def __init__(self, **data):
        self.country = data['country']
        self.currency = data['currency']
        self.full_price = data['full_price']

        self.sales = [Sale(**sale) for sale in data.get('sales', [])]
        self.latest_sale = Sale(**data.get('latest_sale')) if data.get('latest_sale') else None

    @property
    def active(self):
        if not self.latest_sale:
            return None

        if self.latest_sale.discount < 1:
            return None

        return self.latest_sale if self.latest_sale.active else None

    def dump(self):
        tmp = self.__dict__.copy()
        tmp['sales'] = [sale.dump() for sale in self.sales if sale]
        tmp['latest_sale'] = self.latest_sale.dump() if self.latest_sale else None

        return tmp


class Price:

    def __init__(self, **data):
        self._id = data['_id']
        self.game_id = data['game_id']
        self.system = data['system']
        self.region = data['region']

        self.prices = {country: CountryPrice(**price) if price else None
                            for country, price in data.get('prices', {}).items()}

    @property
    def id(self):
        return self._id

    def dump(self):
        tmp = self.__dict__.copy()
        tmp['prices'] = {country: price.dump() if price else None for country, price in self.prices.items()}

        return tmp


class Submission:

    def __init__(self, **data):
        self._id = data['_id']
        self.submission_id = data['submission_id']
        self.subreddit = data['subreddit']
        self.system = data['system']
        self.title = data['title']
        self.url = data.get('url', f'https://redd.it/{self.submission_id}')
        self.length = data.get('length', 0)

        now = datetime.utcnow()
        self.created_at = data.get('created_at', now)
        self.updated_at = data.get('updated_at', now)
        self.expires_at = data.get('expires_at', now + timedelta(days=data.get('days_to_expire', 170)))

    @property
    def id(self):
        return self._id

    def dump(self):
        tmp = self.__dict__.copy()

        return tmp

    def __repr__(self):
        return f'[{self.title}] [{self.subreddit}] [{self.url}]'


class WishlistedGame:

    def __init__(self, **data):
        self._id = data['_id']
        self.countries = data.get('countries', {})

    @property
    def id(self):
        return self._id

    def dump(self):
        tmp = self.__dict__.copy()

        return tmp


class Wishlist:
    def __init__(self, **data):
        self._id = data['_id']
        self.games = {game_id: WishlistedGame(**wg) if wg else None for game_id, wg in data.get('games', {}).items()}

    @property
    def id(self):
        return self._id

    def dump(self):
        tmp = self.__dict__.copy()
        tmp['games'] = {game_id: wg.dump() for game_id, wg in self.games.items()}

        return tmp


class Job:

    LOG = logging.getLogger('jobs')

    def __init__(self, **data):
        self._id = data['_id']
        self.name = data.get('name')
        self.status = data.get('status', 'started')
        self.result = data.get('result')
        self.start = data.get('start', datetime.utcnow())
        self.end = data.get('end', None)
        self.runtime = -1

        Job.LOG.info(f'Running: {self.id}')

    def finish(self, status, result):
        self.status = status
        self.result = result

        self.end = datetime.utcnow()
        self.runtime = (self.end - self.start).seconds

        Job.LOG.info(f'Finish: {self.id} ({self.result})')

    @property
    def id(self):
        return self._id

    def dump(self):
        tmp = self.__dict__.copy()

        return tmp
