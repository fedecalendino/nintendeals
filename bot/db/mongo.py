# Dependencies
from pymongo import MongoClient

# Statics
from bot.commons.config import MONGODB_URI
from bot.commons.keys import *


class Database:

    def __init__(self, collection):
        mongodb = MongoClient(MONGODB_URI)
        database = MONGODB_URI.rsplit('/', 1)[-1]

        self.collection = collection
        self.db = mongodb[database]

    def save(self, obj):
        result = self.load(obj[id_])

        if result:
            self.db[self.collection].update({id_: obj[id_]}, obj)
        else:
            self.db[self.collection].insert(obj)

    def load(self, _id):
        return self.db[self.collection].find_one({id_: _id})

    def load_all(self, filter={}):
        result = []

        for item in self.db[self.collection].find(filter):
            result.append(item)

        return result

    def remove(self, _id):
        self.db[self.collection].remove({id_: _id})


class GamesDatabase(Database):

    _instance = None

    @staticmethod
    def instance():
        if GamesDatabase._instance is None:
            GamesDatabase._instance = GamesDatabase()

        return GamesDatabase._instance

    def __init__(self):
        super(GamesDatabase, self).__init__('games')

    def find_by_region_and_nsuid(self, region, nsuid):
        return self.db[self.collection].find_one({ids_: {region: nsuid}})


class PricesDatabase(Database):

    _instance = None

    @staticmethod
    def instance():
        if PricesDatabase._instance is None:
            PricesDatabase._instance = PricesDatabase()

        return PricesDatabase._instance

    def __init__(self):
        super(PricesDatabase, self).__init__('prices')


class WishlistDatabase(Database):

    _instance = None

    @staticmethod
    def instance():
        if WishlistDatabase._instance is None:
            WishlistDatabase._instance = WishlistDatabase()

        return WishlistDatabase._instance

    def __init__(self):
        super(WishlistDatabase, self).__init__('wishlist')


class RedditDatabase(Database):

    _instance = None

    @staticmethod
    def instance():
        if RedditDatabase._instance is None:
            RedditDatabase._instance = RedditDatabase()

        return RedditDatabase._instance

    def __init__(self):
        super(RedditDatabase, self).__init__('reddit')

    def load_last(self, subreddit, system):
        try:
            result = self.db[self.collection]\
                .find({
                    subreddit_: subreddit,
                    system_: system
                })\
                .sort([(created_at_, -1)])\
                .limit(1)

            return result.next()

        except:
            return None

