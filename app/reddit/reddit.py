# Standard
from datetime import datetime
import logging

# Dependencies
from praw import Reddit as RedditApi

# Modules
from app.db.mongo import PostsDatabase

# Statics
from app.commons.config import *
from app.commons.keys import *


LOG = logging.getLogger('reddit')


class Reddit:

    _instance = None

    @staticmethod
    def instance():
        if Reddit._instance is None:
            Reddit._instance = Reddit()

        return Reddit._instance

    def __init__(self):
        self.api = RedditApi(
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            client_id=REDDIT_CLIENTID,
            client_secret=REDDIT_CLIENTSECRET,
            user_agent=REDDIT_USERAGENT
        )

    def create(self, subreddit, title, content):

        submission = self.api\
            .subreddit(subreddit)\
            .submit(title, selftext=content)

        return submission.id

    def edit(self, submission_id, content):
        submission = self.api.submission(id=submission_id)

        if submission is not None:
            submission.edit(content)

    def delete(self, submission_id):
        submission = self.api.submission(id=submission_id)

        if submission is not None:
            submission.delete()

    def post(self, subreddit, region, system, frequency, title, content, added_games=[]):
        db = PostsDatabase.instance()

        current = db.load_last(subreddit, region, system, frequency)

        text = []

        if len(added_games):
            text.append("---")
            text.append("### Added on {}:".format(datetime.now().date()))
            text.append("")

            for added_game in added_games:
                text.append("* {}".format(added_game))

        text.append("")
        text.append("---")
        text.append("")
        text.append("> Developed by /u/uglyasablasphemy")

        content = content + "\n" + "\n".join(text)

        if current is None:
            current = {
                subreddit_: subreddit,
                region_: region,
                system_: system,
                created_at_: datetime.now()
            }

            sub_id = self.create(subreddit, title.format(region), content)

            current[id_] = sub_id

            db.save(current)

            LOG.info(" Created a new post on {}: https://redd.it/{}".format(subreddit, sub_id))

        else:
            self.edit(current[id_], content)

            current[updated_at_] = datetime.now()
            db.save(current)

            LOG.info(" Updated post on {}: https://redd.it/{}".format(subreddit, current[id_]))
