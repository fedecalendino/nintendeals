from pymongo import MongoClient

from commons.classes import Singleton
from commons.keys import ID
from commons.keys import TITLE
from commons.settings import MONGODB_URI


class Database(metaclass=Singleton):

    def __init__(self, collection):
        mongodb = MongoClient(MONGODB_URI)
        database = MONGODB_URI.rsplit('/', 1)[-1]

        self.collection = collection
        self.db = mongodb[database]

    def save(self, obj):
        result = self.load(obj[ID])

        if result:
            self.db[self.collection].update({ID: obj[ID]}, obj)
        else:
            self.db[self.collection].insert(obj)

    def load(self, _id):
        return self.db[self.collection].find_one({ID: _id})

    def load_all(self, filter={}, sort=[], skip=-1, limit=-1):
        result = self.db[self.collection].find(filter)

        if len(sort):
            result = result.sort(sort)

        if skip >= 0:
            result = result.skip(skip)

        if limit >= 0:
            result = result.limit(limit)

        for item in result:
            yield item

    def count(self, filter={}):
        return self.db[self.collection].find(filter).count()

    def remove(self, _id):
        self.db[self.collection].remove({ID: _id})


class GamesDatabase(Database):

    def __init__(self):
        super(GamesDatabase, self).__init__('games')

    def load_all(self, filter={}, sort=[(TITLE, 1)], skip=-1, limit=-1):
        return super(GamesDatabase, self).load_all(filter, sort, skip, limit)


class PricesDatabase(Database):

    def __init__(self):
        super(PricesDatabase, self).__init__('prices')


class RedditDatabase(Database):

    def __init__(self):
        super(RedditDatabase, self).__init__('reddit')


class WishlistDatabase(Database):

    def __init__(self):
        super(WishlistDatabase, self).__init__('wishlist')
