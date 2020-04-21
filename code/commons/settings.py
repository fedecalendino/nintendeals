import os


MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/nintendeals')


PORT = int(os.environ.get('PORT', 5000))
IP = '127.0.0.1' if PORT == 5000 else '0.0.0.0'


API_KEY = os.environ.get('API_KEY', 'test')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY', 'test')


REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')
REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD')
REDDIT_CLIENTID = os.environ.get('REDDIT_CLIENTID')
REDDIT_CLIENTSECRET = os.environ.get('REDDIT_CLIENTSECRET')
REDDIT_USERAGENT = os.environ.get('REDDIT_USERAGENT')
REDDIT_REFRESH_CODE = os.environ.get('REDDIT_REFRESH_CODE')
REDDIT_REFRESH_TOKEN = os.environ.get('REDDIT_REFRESH_TOKEN')
REDDIT_REDIRECT_URL = os.environ.get('REDDIT_REDIRECT_URL', 'http://localhost:8080')


USER_SUBREDDIT = f'u_{REDDIT_USERNAME}'


POLL = os.environ.get('POLL', None)


WEBSITE_URL = 'http://bot.nintendeals.xyz'


MAINTENANCE = os.environ.get('MAINTENANCE', 'false').lower() == 'true'
