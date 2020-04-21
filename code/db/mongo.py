from pymongo import MongoClient

from commons.classes import Game
from commons.classes import Job
from commons.classes import Price
from commons.classes import Singleton
from commons.classes import Submission
from commons.classes import Wishlist
from commons.keys import ID
from commons.settings import MONGODB_URI


class Database(metaclass=Singleton):

    def __init__(self, collection, clazz):
        mongodb = MongoClient(MONGODB_URI)
        database = MONGODB_URI.rsplit('/', 1)[-1]

        self.db = mongodb[database]
        self.collection = collection
        self.clazz = clazz

    def save(self, obj):
        result = self.load(obj.id)

        if result:
            self.db[self.collection].update({ID: obj.id}, obj.dump())
        else:
            self.db[self.collection].insert(obj.dump())

    def load(self, _id):
        result = self.db[self.collection].find_one({ID: _id})

        return self.clazz(**result) if result else None

    def load_all(self, filter={}, sort=[], skip=-1, limit=-1):
        result = self.db[self.collection].find(filter)

        if len(sort):
            result = result.sort(sort)

        if skip >= 0:
            result = result.skip(skip)

        if limit >= 0:
            result = result.limit(limit)

        for item in result:
            yield self.clazz(**item) if item else None

    def count(self, filter={}):
        return self.db[self.collection].find(filter).count()

    def remove(self, _id):
        self.db[self.collection].remove({ID: _id})


class GamesDatabase(Database):

    def __init__(self):
        super(GamesDatabase, self).__init__('games', Game)

    def load_all(self, filter={}, sort=[('title', 1)], skip=-1, limit=-1):
        return super(GamesDatabase, self).load_all(filter, sort, skip, limit)


class JobDatabase(Database):

    def __init__(self):
        super(JobDatabase, self).__init__('jobs', Job)


class PricesDatabase(Database):

    def __init__(self):
        super(PricesDatabase, self).__init__('prices', Price)


class RedditDatabase(Database):

    def __init__(self):
        super(RedditDatabase, self).__init__('reddit', Submission)


class WishlistDatabase(Database):

    def __init__(self):
        super(WishlistDatabase, self).__init__('wishlists', Wishlist)
