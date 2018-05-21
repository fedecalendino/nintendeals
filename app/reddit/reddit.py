# Standard
import time
from datetime import datetime
import logging

# Dependencies
from praw import Reddit as RedditApi

# Modules
from app.db.mongo import RedditDatabase

# Statics
from app.commons.config import *
from app.commons.keys import *


LOG = logging.getLogger('reddit')


REDDIT_DB = RedditDatabase.instance()


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

        # submission.disable_inbox_replies()

        return submission.id

    def edit(self, submission_id, content):
        submission = self.api.submission(id=submission_id)

        if submission is not None:
            submission.edit(content)

    def delete(self, submission_id):
        submission = self.api.submission(id=submission_id)

        if submission is not None:
            submission.delete()

    def submit(self, subreddit, system, frequency, title, content):
        text = []

        text.append("")
        text.append("---")
        text.append("")
        text.append("* Developed by [uglyasablasphemy](https://www.reddit.com/message/compose?to=uglyasablasphemy&subject=about%20nintendeals%20bot)")
        # text.append("* GitHub repo: https://github.com/federicocalendino/nintendeals")
        text.append("* Last update: {}".format(datetime.now().strftime("%B %d, %H:%M:%S UTC")))
        text.append("* Changes:")
        text.append("")
        text.append("  * Major refactor of the code.")
        text.append("  * Pushed code to github (pm /u/uglyasablasphemy for repo).")
        text.append("  * All countries' deals list are replies to one top level comment.")
        text.append("  * Fixed bug (all games on sale should appear correctly now).")
        text.append("  * Changed how the metacritic scores are displayed.Also, if there are no scores for switch, the bot will lookup for the pc version.")

        content = content + "\n" + "\n".join(text)

        current = REDDIT_DB.load_last(subreddit, system, frequency)

        if current is not None and self.exists(current[id_]) is None:
            current = None

        if current is None:
            LOG.info(" Submitting to /r/{}".format(subreddit))

            current = {
                subreddit_: subreddit,
                system_: system,
                created_at_: datetime.now()
            }

            sub_id = self.create(subreddit, title, content)
            current[id_] = sub_id

            LOG.info(" Submitted to /r/{}: https://redd.it/{}".format(subreddit, sub_id))

            time.sleep(5)

            comment = self.api.submission(id=sub_id).reply('🔥⬇️ DEALS LISTS ⬇️🔥')
            current[main_comment_] = comment.id

            LOG.info(" Added main comment: https://reddit.com/comments/{}/_/{}".format(sub_id, comment.id))

            REDDIT_DB.save(current)
        else:
            LOG.info(" Updating submission on /r/{}".format(subreddit))

            if comments_ in current:
                links = []

                for country, country_details in COUNTRIES.items():
                    if country in current[comments_]:
                        links.append(
                            '[{flag} {name}](https://reddit.com/comments/{sub_id}/_/{comment_id}/?context=2)'.format(
                                flag=country_details[flag_],
                                name=country,
                                sub_id=current[id_],
                                comment_id=current[comments_][country]
                            )
                        )

                content = 'Shortcuts: {}\n___\n{}'.format(' | '.join(links), content)

            self.edit(current[id_], content)

            current[updated_at_] = datetime.now()
            REDDIT_DB.save(current)

            LOG.info(" Updated submission on /r/{}: https://redd.it/{}".format(subreddit, current[id_]))

        return current[id_]

    def comment(self, sub_id, country, content):
        submission = REDDIT_DB.load(sub_id)
        main_comment_id = submission[main_comment_]

        if comments_ not in submission:
            submission[comments_] = {}

        if country not in submission[comments_]:
            comment = self.api.comment(id=main_comment_id).reply(content)
            submission[comments_][country] = comment.id

            LOG.info("Created comment https://reddit.com/comments/{}//{}".format(sub_id, comment.id))
        else:
            comment_id = submission[comments_][country]
            self.api.comment(comment_id).edit(content)

            LOG.info("Updated comment https://reddit.com/comments/{}//{}".format(sub_id, comment_id))

        REDDIT_DB.save(submission)

