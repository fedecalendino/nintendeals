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

    def post(self, subreddit, system, frequency, title, content):
        db = PostsDatabase.instance()

        text = []

        text.append("")
        text.append("---")
        text.append("")
        text.append("* Developed by [uglyasablasphemy]"
                    "(https://www.reddit.com/message/compose?to=uglyasablasphemy&subject=comments%20for%20the%20nintendeals%20bot)")
        text.append("* Last update: {}".format(datetime.now().strftime("%B %d, %H:%M:%S UTC")))

        text.append("")
        text.append("---")
        text.append("")
        text.append("FAQ:")
        text.append("Why did you changed the format?")
        text.append("> When the ammount of deals increase i had to take countries out to be able to show everything on one post,")
        text.append("> with this new format i can include as many countries as you like. This solution will scale in the future, no matter ")
        text.append("> how many deals are active on a give time.")
        text.append("> note: after the comments are created a list of quick links will be added on top of the post for you to get to your country without scrolling.")
        text.append("> **If you don't like the discount/country table on the post, i'd love to hear some feedback to improve it or change it.**")
        text.append("")
        text.append("Why is there a 0 after some prices?")
        text.append("> This is to be able to sort correctly using the sorters in the reddit tables. [Example](https://www.reddit.com/r/NintendoSwitchDeals/comments/8i0ofo/current_nintendo_switch_eshop_deals/dyoaouj/)")
        text.append("")
        text.append("Why is there lot of games that seem to be always on discount?")
        text.append("> Some devs seem to exploit the deal system to gain more exposure. Once i have enough historical data on prices")
        text.append("> i'll be able to detect them and filtering them out.")

        content = content + "\n" + "\n".join(text)

        print("")
        print("")
        print(content)
        print("")
        print("")

        current = db.load_last(subreddit, system, frequency)

        if current is not None and self.exists(current[id_]) is None:
            current = None

        if current is None:
            LOG.info(" Creating a post on {}".format(subreddit))

            current = {
                subreddit_: subreddit,
                system_: system,
                created_at_: datetime.now()
            }

            sub_id = self.create(subreddit, title, content)

            current[id_] = sub_id

            db.save(current)

            LOG.info(" Created a new post on {}: https://redd.it/{}".format(subreddit, sub_id))

        else:
            LOG.info(" Updating post on {}".format(subreddit))

            if comments_ in current:
                links = []

                for country, country_details in COUNTRIES.items():
                    if country in current[comments_]:
                        links.append(
                            '[{flag} {name}](https://reddit.com/comments/{post_id}/_/{comment_id})'.format(
                                flag=country_details[flag_],
                                name=country,
                                post_id=current[id_],
                                comment_id=current[comments_][country]
                            )
                        )

                content = 'Quick links: {}\n___\n{}'.format(' | '.join(links), content)

            self.edit(current[id_], content)

            current[updated_at_] = datetime.now()
            db.save(current)

            LOG.info(" Updated post on {}: https://redd.it/{}".format(subreddit, current[id_]))

        return current[id_]

    def comment(self, post_id, country, content):
        db = PostsDatabase.instance()
        post = db.load(post_id)

        print("")
        print("")
        print(content)
        print("")
        print("")

        if comments_ not in post:
            post[comments_] = {}

        if country not in post[comments_]:
            comment = self.api.submission(id=post_id).reply(content)
            post[comments_][country] = comment.id

            LOG.info("Created comment https://reddit.com/comments/{}//{}".format(post_id, comment.id))
        else:
            comment_id = post[comments_][country]
            self.api.comment(comment_id).edit(content)

            LOG.info("Updated comment https://reddit.com/comments/{}//{}".format(post_id, comment_id))

        db.save(post)

