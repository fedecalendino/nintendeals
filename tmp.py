from nintendeals.api import prices
from nintendeals.noa import listing

games = list(listing.list_games("Nintendo Switch"))
prices = prices.get_prices("US", games)

print("")