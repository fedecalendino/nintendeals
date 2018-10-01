from bot.commons.keys import title_, games_

from bot.db.mongo import GamesDatabase
from bot.db.mongo import WishlistDatabase

from bot.commons.util import get_title


GAMES_DB = GamesDatabase.instance()
WISHLIST_DB = WishlistDatabase.instance()

counts = {}

wishlists = WISHLIST_DB.load_all()
total_users = len(wishlists)

for wishlist in wishlists:
    for game_id in wishlist[games_]:
        if game_id not in counts:
            game = GAMES_DB.load(game_id)

            if game is None:
                continue

            counts[game_id] = {
                'count': 0,
                title_: get_title(game)
            }

        counts[game_id]['count'] += 1


totals = sorted(counts.values(), key=lambda x: x['count'], reverse=True)

print('###Wishlisted games: {}'.format(len(totals)))
print('###Total users: {}'.format(total_users))

print()
print()

print('###Top 50')
print()
print('title | total | %')
print('--- | :---: | :---:')

for total in totals[:50]:
    count = total['count']
    print('{}|{}|{}%'.format(
        total[title_],
        count,
        int(100 * count/total_users)))
