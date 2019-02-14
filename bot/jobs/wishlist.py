import logging

from bot.wishlist import wishlist


LOG = logging.getLogger('jobs.wishlist')


def notify_users():
    wishlist.notify_users()
