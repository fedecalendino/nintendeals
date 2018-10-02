# Standard
import time
from datetime import datetime
from datetime import timedelta
import logging

# Dependencies
from praw import Reddit as RedditApi

# Modules
from bot.db.util import load_all_games
from bot.db.mongo import GamesDatabase
from bot.db.mongo import RedditDatabase
from bot.db.mongo import WishlistDatabase

# Statics
from bot.commons.config import *
from bot.commons.keys import *
from bot.commons.util import *


LOG = logging.getLogger('🌐')

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
                LOG.info(' https://redd.it/{}: deleted'.format(post[id_]))
                return False

            created_at = post[created_at_]

            # Checking if archived
            if created_at + timedelta(days=30 * 5) < datetime.now():
                LOG.info(' https://redd.it/{}: archived'.format(post[id_]))
                return False

            # Checking if stickied
            if submission.stickied:
                LOG.info(' https://redd.it/{}: stickied'.format(post[id_]))
                return True

            now = datetime.now()

            if now.today().weekday() not in [0, 3]:  # now is not monday/thursday
                LOG.info(' https://redd.it/{}: not monday/thursday yet'.format(post[id_]))
                return True
            elif now.hour < 16:
                LOG.info(' https://redd.it/{}: not 16:00 yet'.format(post[id_]))
                return True
            elif created_at.day != now.day:
                LOG.info(' https://redd.it/{}: *its monday/thursday my dudes*'.format(post[id_]))
                submission.mod.nsfw()
                LOG.info(' https://redd.it/{}: marked as nsfw'.format(post[id_]))

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
        text = []
        text.append('Testing new format, do you like it? > https://strawpoll.com/fd1bze72')
        text.append('___')

        if system == SWITCH_:
            text.append('⭐Add games to your WISHLIST ⭐: {}'.format(WISHLIST_URL))
            text.append('> You\'ll get a PM when a wishlisted game is discounted.')
            text.append('')
            text.append('___')
            text.append('')

        text.append(content)

        text.append('')
        text.append('___')
        text.append('')

        text.append('* Developed by /u/uglyasablasphemy | [Switch Friend Code](https://nin.codes/uglyasablasphemy)')

        text.append('* Use [RES](https://redditenhancementsuite.com) for table sorting and more')
        text.append('* If you have perfomance issues, you might want to check out:')
        text.append('   * [Reddit is Fun](https://play.google.com/store/apps/details?id=com.andrewshu.android.reddit)')
        text.append('   * [Apollo for Reddit](https://itunes.apple.com/us/app/apollo-for-reddit/id979274575)')
        text.append('')
        text.append('___')
        text.append('Testing new format, do you like it? > https://strawpoll.com/fd1bze72')

        current = REDDIT_DB.load_last(subreddit, system)

        if current is not None and not self.usable(current):
            current = None

        if current is None:
            LOG.info(' Submitting to /r/{}'.format(subreddit))

            current = {
                subreddit_: subreddit,
                system_: system,
                created_at_: datetime.now()
            }

            sub_id = self.create(subreddit, title, '\n'.join(text))
            current[id_] = sub_id

            LOG.info(' Submitted to /r/{}: https://redd.it/{}'.format(subreddit, sub_id))

            time.sleep(5)

            comment = self.api.submission(id=sub_id).reply('🔥⬇️ DEALS LISTS ⬇️🔥')
            current[main_comment_] = comment.id

            LOG.info(' Added main comment: https://reddit.com/comments/{}/_/{}'.format(sub_id, comment.id))

            REDDIT_DB.save(current)
        else:
            LOG.info(' Updating submission on /r/{}'.format(subreddit))

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

                text.insert(0, '#For more information, click on your country/region')
                text.insert(1, ' | '.join(links))
                text.insert(2, ('---|' * len(links))[:-1])
                text.insert(3, '___')

                self.edit(current[id_], '\n'.join(text))

            current[updated_at_] = datetime.now()
            REDDIT_DB.save(current)

            LOG.info(' Updated submission on /r/{}: https://redd.it/{}'.format(subreddit, current[id_]))

        return current[id_]

    def comment(self, sub_id, country, content):
        LOG.info('Trying to comment on {} {}: {}'.format(sub_id, country, len(content)))

        submission = REDDIT_DB.load(sub_id)
        main_comment_id = submission[main_comment_]

        if comments_ not in submission:
            submission[comments_] = {}

        if country not in submission[comments_]:
            comment = self.api.comment(id=main_comment_id).reply(content)
            submission[comments_][country] = comment.id

            LOG.info('Created comment https://reddit.com/comments/{}//{} ({})'.format(sub_id, comment.id, country))
        else:
            comment_id = submission[comments_][country]
            self.api.comment(comment_id).edit(content)

            LOG.info('Updated comment https://reddit.com/comments/{}//{} ({})'.format(sub_id, comment_id, country))

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

            try:
                spl = message.subject.split(' : ')
                command = spl[0]
                game_id = spl[1]
            except:
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
        message = self.make_response(username, content)

        if len(message) > 10000:
            message = self.make_response(username, content, exclude_wishlist=True)

        try:
            self.api.redditor(username).message(title, message)

            time.sleep(10)
        except:
            LOG.error('Error sending to {}: {}'.format(username, len(content)))

    def reply(self, message, content):
        username = message.author.name

        content = self.make_response(username, content)

        message.reply(content)
        message.mark_read()

    def make_response(self, username, content, exclude_wishlist=False):
        text = []
        text.append('##Hi {}'.format(username))
        text.append('')
        text.append(content)
        text.append('')
        text.append('___')
        text.append('')

        user = WISHLIST_DB.load(username)

        if not exclude_wishlist:
            if user is None or games_ not in user or len(user[games_]) is 0:
                text.append('###Your wishlist is empty'.format(username))

            else:
                text.append('###Your current wishlist:'.format(username))

                text.append('')
                text.append('Title | Countries | Actions')
                text.append('--- | --- | :---: ')

                for game in load_all_games(filter={id_: {'$in': list(user[games_].keys())}}, exclude_prices=True):
                    game_id = game[id_]
                    title = get_title(game)

                    country_list = []

                    for country in user[games_][game_id][countries_]:
                        country_details = COUNTRIES[country]
                        country_list.append('{} {}'.format(country_details[flag_], country_details[key_]))

                    text.append(
                        '{}|{}|{}'.format(
                            title,
                            ' '.join(country_list),
                            '[{emoji}](//reddit.com/message/compose?to={to}&subject={cmd} : {game_id}&message={body})'.format(
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
        countries = [country for country in message.body.split(' ') if len(country) > 1]

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
        title = get_title(game)

        if game_id not in wishlist[games_]:
            wishlist[games_][game_id] = {}

        countries = sorted(list(countries))

        wishlist[games_][game_id][countries_] = countries
        wishlist[games_][game_id][last_update_] = datetime.now()

        WISHLIST_DB.save(wishlist)

        self.reply(message, '*{}* was added to your wishlist :)'.format(title))

        LOG.info('📥 > {} wishlisted {} for {}'.format(username, title, ', '.join(countries)))

    def wishlist_remove(self, message, username, game):

        game_id = game[id_]
        title = get_title(game)

        wishlist = WISHLIST_DB.load(username)

        if wishlist is None or game_id not in wishlist[games_]:
            self.reply(message, '`Error`: {} is not on your wishlist'.format(title))

        del wishlist[games_][game_id]

        WISHLIST_DB.save(wishlist)

        self.reply(message, '*{}* was deleted from your wishlist :('.format(title))

        LOG.info('📥 > {} deleted {}'.format(username, title))

