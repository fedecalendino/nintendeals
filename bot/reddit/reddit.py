# Standard
import time
from datetime import datetime
from datetime import timedelta
import logging

# Dependencies
from praw import Reddit as RedditApi

# Modules
from bot.db.mongo import GamesDatabase
from bot.db.mongo import RedditDatabase
from bot.db.mongo import WishlistDatabase

# Statics
from bot.commons.config import *
from bot.commons.keys import *


LOG = logging.getLogger('reddit')

GAMES_DB = GamesDatabase.instance()
REDDIT_DB = RedditDatabase.instance()
WISHLIST_DB = WishlistDatabase.instance()


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

    def usable(self, post):
        try:
            submission = self.api.submission(id=post[id_])

            # Checking for deletion
            if submission.author.name != REDDIT_USERNAME:
                LOG.info(" https://redd.it/{}: deleted".format(post[id_]))
                return False

            created_at = post[created_at_]

            # Checking if archived
            if created_at + timedelta(days=30 * 5) < datetime.now():
                LOG.info(" https://redd.it/{}: archived".format(post[id_]))
                return False

            # Checking if stickied
            if submission.stickied:
                LOG.info(" https://redd.it/{}: stickied".format(post[id_]))
                return True

            now = datetime.now()

            if now.today().weekday() != 3:  # now is not thursday
                LOG.info(" https://redd.it/{}: not thursday yet".format(post[id_]))
                return True
            elif now.hour < 17:  # now is not 14 yet
                LOG.info(" https://redd.it/{}: not 14:00 yet".format(post[id_]))
                return True
            elif created_at.day != now.day:
                LOG.info(" https://redd.it/{}: old post, *its thursday my dudes*".format(post[id_]))
                return False

        except Exception as e:
            return False

        return True

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

    def submit(self, subreddit, system, title, content):
        header = ['']

        if system == SWITCH_:
            header.append("⭐ NEW FEATURE: WISHLIST ⭐")
            header.append("")
            header.append("For more information you can go to: {}".format(WISHLIST_URL))
            header.append("")
            header.append("---")
            header.append("")

        footer = []

        footer.append("")
        footer.append("---")
        footer.append("")
        footer.append("* Developed by /u/uglyasablasphemy")
        footer.append("* Consider using RES for table sorting: https://redditenhancementsuite.com")

        content = "\n".join(header) + content + "\n" + "\n".join(footer)

        current = REDDIT_DB.load_last(subreddit, system)

        if current is not None and not self.usable(current):
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

                content = 'Detailed information here -->> {}\n___\n{}'.format(' | '.join(links), content)

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

    def inbox(self):
        for message in self.api.inbox.all(limit=50):
            if message.was_comment:
                continue

            if not message.new:
                continue

            valid_command = False

            for command in [CMD_ADD, CMD_REMOVE, CMD_LIST]:
                if message.subject.startswith(command):
                    valid_command = True

            if not valid_command:
                continue

            if message.subject.startswith(CMD_LIST):
                self.reply(message, '')
                continue

            command, game_id = message.subject.split(': ')

            if game_id is None:
                self.reply(message, '`Error`: missing game id on subject.')
                continue

            game = GAMES_DB.load(game_id)

            if game is None:
                self.reply(message, '`Error`: game with id {} was not found.'.format(game_id))
                continue

            username = message.author.name

            if command == CMD_ADD:
                self.wishlist_add(message, username, game)
            elif command == CMD_REMOVE:
                self.wishlist_remove(message, username, game)

    def send(self, username, title, content):
        content = self.make_response(username, content)

        self.api.redditor(username).message(title, content)

        time.sleep(10)

    def reply(self, message, content):
        username = message.author.name

        content = self.make_response(username, content)

        message.reply(content)
        message.mark_read()

    def make_response(self, username, content):
        text = []
        text.append('##Hi {}'.format(username))
        text.append('')
        text.append(content)
        text.append('')
        text.append('___')
        text.append('')

        obj = WISHLIST_DB.load(username)

        if obj is None or games_ not in obj or len(obj[games_]) is 0:
            text.append('###Your wishlist is empty'.format(username))

        else:
            text.append('###Your current wishlist:'.format(username))

            text.append('')
            text.append('Title | Countries | Actions')
            text.append('--- | --- | :---: ')

            for game_id, game_details in obj[games_].items():
                game = GAMES_DB.load(game_id)

                if title_ in game:
                    title = game[title_]
                else:
                    title = game[title_jp_]

                country_list = []

                for country in game_details[countries_]:
                    country_details = COUNTRIES[country]

                    country_list.append('{} {}'.format(country_details[flag_], country_details[key_]))

                text.append(
                    '{}|{}|{}'.format(
                        title,
                        ' '.join(country_list),
                        '[{emoji}](http://www.reddit.com/message/compose?to={to}&subject={cmd}: {game_id}&message={body})'.format(
                            cmd=CMD_REMOVE, emoji=EMOJI_MINUS, to=REDDIT_USERNAME, game_id=game_id, body='.'),
                    )
                )

        text.append('___')
        text.append('Add games to your wishlist [HERE]({}).'.format(WISHLIST_URL))
        text.append('')

        text.append('Check the latest deals on:')
        text.append('')

        system_details = SYSTEMS[SWITCH_]
        for subreddit in system_details[subreddit_]:
            current = REDDIT_DB.load_last(subreddit, SWITCH_)

            if current is None:
                continue

            text.append(
                '* [/r/{}](https://redd.it/{})'.format(subreddit, current[id_])
            )

        text.append('')

        return '\n'.join(text)

    def wishlist_add(self, message, username, game):
        countries = message.body.split(' ')

        invalid_countries = []

        for country in countries:
            if country not in COUNTRIES.keys():
                invalid_countries.append(country)

        if len(invalid_countries) != 0:
            self.reply(message, '`Error`: {} are not valid countries.'.format(', '.join(invalid_countries)))
            return

        wishlist = WISHLIST_DB.load(username)

        if wishlist is None:
            wishlist = {
                id_: username,
                games_: {}
            }

        limit = 50

        if len(wishlist[games_]) >= limit:
            self.reply(message, '`Error`: a maximum of {} wishlisted games has been reached.'.format(limit))
            return

        game_id = game[id_]

        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        if game_id not in wishlist[games_]:
            wishlist[games_][game_id] = {}

        countries = sorted(list(countries))

        wishlist[games_][game_id][countries_] = countries
        wishlist[games_][game_id][last_update_] = datetime.now()

        WISHLIST_DB.save(wishlist)

        self.reply(message, '*{}* was added to your wishlist :)'.format(title))

        LOG.info('{} wishlisted {}'.format(username, title))

    def wishlist_remove(self, message, username, game):

        game_id = game[id_]

        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        wishlist = WISHLIST_DB.load(username)

        if wishlist is None or game_id not in wishlist[games_]:
            self.reply(message, '`Error`: {} is not on your wishlist'.format(title))

        del wishlist[games_][game_id]

        WISHLIST_DB.save(wishlist)

        self.reply(message, '*{}* was deleted from your wishlist :('.format(title))

        LOG.info('{} deleted {}'.format(username, title))

