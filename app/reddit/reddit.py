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

    def exists(self, submission_id):
        try:
            submission = self.api.submission(id=submission_id)

            if submission.author.name == REDDIT_USERNAME:
                return submission
            else:
                return None
        except Exception as e:
            return None

    def create(self, subreddit, title, content):

        submission = self.api\
            .subreddit(subreddit)\
            .submit(title, selftext=content)

        submission.disable_inbox_replies()

        return submission.id

    def edit(self, submission_id, content):
        submission = self.api.submission(id=submission_id)

        if submission is not None:
            submission.edit(content)

    def delete(self, submission_id):
        submission = self.api.submission(id=submission_id)

        if submission is not None:
            submission.delete()

    def post(self, subreddit, region, system, frequency, title, content):
        db = PostsDatabase.instance()

        symbols = '> `{} > new` `{} > expires soon` `{} > expires in less than 24h` `{} > best discount in {}`'\
            .format(EMOJI_NEW, EMOJI_EXP_TOMORROW, EMOJI_EXP_TODAY, EMOJI_MAX_DISCOUNT, region)

        text = []

        text.append("")
        text.append("---")
        text.append("")
        text.append("* Developed by [uglyasablasphemy]"
                    "(https://www.reddit.com/message/compose?to=uglyasablasphemy&subject=comments%20for%20ther%20nintendeals%20bot)")
        text.append("* Last update: {}".format(datetime.now().strftime("%B %d, %H:%M:%S UTC")))
        text.append("")
        text.append("* Changelog ({}):".format(VERSION))
        text.append("  * Added a column for the number of players.")
        text.append("  * Compacted the sale and full price columns into one.")
        text.append("  * Added icons on top of the post.")
        text.append("  * Added the {} symbol to indicate the best discount in the region.".format(EMOJI_MAX_DISCOUNT))

        content = symbols + "\n" + content + "\n" + "\n".join(text)

        current = db.load_last(subreddit, region, system, frequency)

        if current is not None and self.exists(current[id_]) is None:
            current = None

        if current is None:
            LOG.info(" Creating a post on {}".format(subreddit))

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
            LOG.info(" Updating post on {}".format(subreddit))

            self.edit(current[id_], content)

            current[updated_at_] = datetime.now()
            db.save(current)

            LOG.info(" Updated post on {}: https://redd.it/{}".format(subreddit, current[id_]))
