from nintendeals import noe as nin

for game in nin.list_games("Nintendo Switch"):
    print(game.nsuid)
    all_info = nin.game_info(game.nsuid)

    if all_info:
        print(all_info.title)
