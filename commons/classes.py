from commons.config import COUNTRIES
from commons.config import REGIONS
from commons.keys import CATEGORIES
from commons.keys import ID
from commons.keys import LAST_UPDATE
from commons.keys import METASCORE
from commons.keys import NSUIDS
from commons.keys import NUMBER_OF_PLAYERS
from commons.keys import PUBLISHED_BY_NINTENDO
from commons.keys import RELEASE_DATE
from commons.keys import SCORES
from commons.keys import SYSTEM
from commons.keys import TITLE
from commons.keys import TITLE_EN
from commons.keys import TITLE_JP
from commons.keys import USERSCORE
from commons.keys import WEBSITES
from commons.keys import WISHLISTED


class Game(dict):

    @staticmethod
    def create(game_id, system):
        game = Game({})

        game[ID] = game_id
        game[SYSTEM] = system

        game.set_defaults()

        return game

    def set_defaults(self):

        for key in [TITLE, TITLE_EN, TITLE_JP, RELEASE_DATE]:
            self.setdefault(key)

        self.setdefault(CATEGORIES, [])
        self.setdefault(NUMBER_OF_PLAYERS, 0)
        self.setdefault(WISHLISTED, 0)
        self.setdefault(PUBLISHED_BY_NINTENDO, False)

        for key in [SCORES, NSUIDS, WEBSITES]:  # , REDDIT]:
            self.setdefault(key, {})

        for key in [METASCORE, USERSCORE, LAST_UPDATE]:
            self[SCORES].setdefault(key)

        for region in REGIONS:
            self[NSUIDS].setdefault(region)

        for country, details in COUNTRIES.items():
            if WEBSITES in details:
                self[WEBSITES].setdefault(country)

        return self


class Singleton(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)

        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)

        return cls._instance
