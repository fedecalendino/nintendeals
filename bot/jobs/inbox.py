import logging
from bot.reddit import Reddit
from bot.wishlist import generator

from bot.wishlist.wishlist import add as wl_add
from bot.wishlist.wishlist import remove as wl_remove
from bot.wishlist.wishlist import show as wl_show
from bot.wishlist.wishlist import delete as wl_delete
from bot.wishlist.constants import SEPARATOR
from bot.wishlist.constants import WL_ADD
from bot.wishlist.constants import WL_DELETE
from bot.wishlist.constants import WL_LIST
from bot.wishlist.constants import WL_REMOVE
from bot.wishlist.constants import WL_SHOW


LOG = logging.getLogger('inbox')


COMMANDS = {
    WL_ADD: wl_add,
    WL_REMOVE: wl_remove,
    WL_LIST: wl_show,
    WL_SHOW: wl_show,
    WL_DELETE: wl_delete,
}


def unknown(message, _):
    return None


def check():
    LOG.info('checking inbox')
    reddit = Reddit()

    for message in reddit.inbox():
        subject = message.subject.replace('Switch-', 'NX/').upper()

        split = subject.split(SEPARATOR)

        command = COMMANDS.get(split[0], unknown)
        content = command(message, split[1] if len(split) > 1 else None)

        if not content:
            continue

        body = [
            generator.generate_header(message.author.name),
            '',
            '',
            content,
            '___',
            generator.build_wishlist(message.author.name),
            '___',
            generator.generate_footer()
        ]

        reddit.reply(message, '\n'.join(body))
