import os


MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/nintendeals')


PORT = int(os.environ.get('PORT', 5000))
IP = '127.0.0.1' if PORT == 5000 else '0.0.0.0'


REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME', 'uglyasablasphemy')
REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD', 'XpwZ*^E3t8jqx!iC')
REDDIT_CLIENTID = os.environ.get('REDDIT_CLIENTID', 'W9Ju_rDalSz60A')
REDDIT_CLIENTSECRET = os.environ.get('REDDIT_CLIENTSECRET', 'aiwFY48uC8H72-ri-F2rOfhrjAM')
REDDIT_USERAGENT = os.environ.get('REDDIT_USERAGENT', 'nintendo deals automated bot')

USER_SUBREDDIT = f'u_{REDDIT_USERNAME}'


POLL = os.environ.get('POLL', None)


WISHLIST_URL = 'https://nintendeals.herokuapp.com/'
