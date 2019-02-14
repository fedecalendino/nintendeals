import logging
from datetime import datetime
from datetime import timedelta
from time import sleep

from praw import Reddit as RedditApi

from db.mongo import RedditDatabase

from commons.classes import Singleton
from commons.keys import CREATED_AT
from commons.keys import EXPIRES_AT
from commons.keys import ID
from commons.keys import SUBMISSION_ID
from commons.keys import SUBREDDIT
from commons.keys import SYSTEM
from commons.keys import TITLE
from commons.keys import UPDATED_AT
from commons.keys import URL
from commons.settings import REDDIT_CLIENTID
from commons.settings import REDDIT_CLIENTSECRET
from commons.settings import REDDIT_PASSWORD
from commons.settings import REDDIT_USERAGENT
from commons.settings import REDDIT_USERNAME


LOG = logging.getLogger('reddit')


def sub_to_str(sub):
    return f'[{sub[TITLE]}] [{sub[SUBREDDIT]}] [{sub[URL]}]'


class Reddit(metaclass=Singleton):

    def __init__(self):
        self.api = RedditApi(
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            client_id=REDDIT_CLIENTID,
            client_secret=REDDIT_CLIENTSECRET,
            user_agent=REDDIT_USERAGENT
        )

    def usable(self, sub, country=False):
        now = datetime.utcnow()

        if not sub.get(SUBMISSION_ID):
            return False

        try:
            submission = self.api.submission(id=sub[SUBMISSION_ID])

            if not submission.author or submission.author.name != REDDIT_USERNAME:
                LOG.info(f'Submission was deleted: {sub_to_str(sub)}')
                return False

            if country and sub[EXPIRES_AT] > now:
                LOG.info(f'Submission expired: {sub_to_str(sub)}')
                return False

            if submission.stickied:
                LOG.info(f'Submission is stickied: {sub_to_str(sub)}')
                return True

            if now.today().weekday() not in [0, 3]:  # now is not monday/thursday
                LOG.info(f'Submission will be reused (not monday/thursday yet): {sub_to_str(sub)}')
                return True

            if now.hour < 17:
                LOG.info(f'Submission will be reused (not 17:00 UTC yet): {sub_to_str(sub)}')
                return True

            if sub[CREATED_AT].day != now.day:
                LOG.info(f'Submission will be replaced (it\'s monday/thursday, my dudes): {sub_to_str(sub)}')
                return False
        except Exception as e:
            LOG.error(f'Submission shows error {str(e)}, will be replaced: {sub_to_str(sub)}')
            return False

        LOG.info(f'Submission will be reused: {sub_to_str(sub)}')
        return True

    def create(self, subreddit, title, content):
        submission = self.api\
            .subreddit(subreddit)\
            .submit(title, selftext=content)

        submission.disable_inbox_replies()

        return submission.id

    def edit(self, sub, content):
        submission = self.api.submission(id=sub[SUBMISSION_ID])

        if not submission:
            return

        try:
            submission.edit(content)
            LOG.info(f'Submission updated: {sub_to_str(sub)}')
        except:
            LOG.error(f'Submission can\'t be edited: {sub_to_str(sub)}')

    def nsfw(self, sub):
        submission = self.api.submission(id=sub[SUBMISSION_ID])

        if not submission:
            return

        try:
            submission.mod.nsfw()
            LOG.info(f'Submission marked as NSFW: {sub_to_str(sub)}')
        except:
            LOG.error(f'Submission can\'t be marked as NSFW: {sub_to_str(sub)}')

    def submit(self, system, subreddit, title, content, country=None):
        reddit_db = RedditDatabase()

        key = f'{system}/{country if country else subreddit}'
        sub = reddit_db.load(key)

        if not sub:
            sub = {
                ID: key
            }

        now = datetime.utcnow()

        if not self.usable(sub):
            if sub.get(SUBMISSION_ID):
                self.nsfw(sub)

            submission_id = self.create(subreddit, title, content)

            sub[SUBMISSION_ID] = submission_id
            sub[CREATED_AT] = now
            sub[EXPIRES_AT] = now + timedelta(days=14 if country else 170)
            sub[SUBREDDIT] = subreddit
            sub[SYSTEM] = system
            sub[TITLE] = title
            sub[URL] = f'https://redd.it/{submission_id}'

            LOG.info(f'Submission created: {sub_to_str(sub)}')
        else:
            sub[UPDATED_AT] = now
            self.edit(sub, content)

        reddit_db.save(sub)

        sleep(5)

        return sub

    def inbox(self):
        return [message for message in self.api.inbox.unread() if not message.was_comment]

    def send(self, username, title, content):
        try:
            LOG.info('Sending to {}: {}'.format(username, title))

            self.api.redditor(username).message(title, content)
            sleep(10)
        except:
            LOG.error('Error sending to {}: {}'.format(username, title))

    def reply(self, message, content):
        try:
            LOG.info('Replying to {}: {}'.format(message.author.name, message.subject))

            message.reply(content)
            message.mark_read()
            sleep(10)
        except:
            LOG.error('Error replying to {}: {}'.format(message.author.name, message.subject))
