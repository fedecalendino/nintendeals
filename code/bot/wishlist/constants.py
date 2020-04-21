from commons.emoji import WARNING

from commons.settings import REDDIT_USERNAME


SEPARATOR = ' : '


WL_ADD = 'ADD'
WL_REMOVE = 'REMOVE'
WL_SHOW = 'SHOW'
WL_LIST = 'LIST'
WL_DELETE = 'DELETE'


GAME_ADDED = '###{} was added to your wishlist 😄'
GAME_REMOVED = '###{} was deleted from your wishlist'

WISHLIST_SHOWED = '###Here is your current wishlist 😄'
WISHLIST_EMPTY = '###Your wishlist is empty'
WISHLIST_FULL = '###Your wishlist is full ({}/{} games)'
WISHLIST_DELETED = '###Your wishlist was deleted ☹️'

INVALID_GAME_ID = '###The game id {} is not valid'
INVALID_COUNTRY = '###The country {} is not valid'
INVALID_COUNTRIES = '###The countries {} are not valid'
INVALID_WISHLISTED_GAME = '###The game {} isn\'t on your wishlist'

NO_WISHLIST = f'###You don\'t have a wishlist'

GAMES_ON_SALE = 'Wishlisted games on sale!'


ADD_URL = f'https://www.reddit.com/message/compose?to={REDDIT_USERNAME}' \
          f'&subject={WL_ADD}{SEPARATOR}{{}}{SEPARATOR}{{}}' \
          f'&message={{}}'

DELETE_URL = f'https://www.reddit.com/message/compose?to={REDDIT_USERNAME}' \
          f'&subject={WL_DELETE}' \
          f'&message={WARNING}This will delete your wishlist, if you are sure send the message.{WARNING}'

SHOW_URL = f'https://www.reddit.com/message/compose?to={REDDIT_USERNAME}' \
          f'&subject={WL_SHOW}' \
          f'&message=.'

REMOVE_URL = f'https://www.reddit.com/message/compose?to={REDDIT_USERNAME}' \
          f'&subject={WL_REMOVE}{SEPARATOR}{{}}' \
          f'&message=.'
