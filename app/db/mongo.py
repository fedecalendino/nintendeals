# Standard
from datetime import timedelta
from datetime import datetime

# Dependencies
from pymongo import MongoClient

# Statics
from app.commons.config import MONGODB_URI
from app.commons.keys import *


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


class PostsDatabase(Database):

    _instance = None

    @staticmethod
    def instance():
        if PostsDatabase._instance is None:
            PostsDatabase._instance = PostsDatabase()

        return PostsDatabase._instance

    def __init__(self):
        super(PostsDatabase, self).__init__('posts')

    def load_last(self, subreddit, system, frequency):
        try:
            result = self.db[self.collection]\
                .find({
                    subreddit_: subreddit,
                    system_: system
                })\
                .sort([(created_at_, -1)])\
                .limit(1)

            post = result.next()

            if post[created_at_] + timedelta(days=frequency) < datetime.now():
                return None

            return post
        except:
            return None

