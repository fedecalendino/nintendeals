from datetime import datetime
from typing import Dict

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Features, Platforms, Ratings, Regions

PLATFORMS = {
    "4_WUP": Platforms.NINTENDO_WIIU,
    "2_CTR": Platforms.NINTENDO_3DS,
    "3_KTR": Platforms.NINTENDO_3DS,
    "1_HAC": Platforms.NINTENDO_SWITCH,
}

RATINGS = {
    "0": None,
    "1": "A",
    "2": "B",
    "3": "C",
    "4": "D",
    "5": "Z",
}


def build_game(data: Dict) -> Game:
    hard = data.get("hard")
    icode = data.get("icode")

    if hard and icode:
        product_code = hard[2:] + icode
    else:
        product_code = None

    game = Game(
        platform=PLATFORMS[hard],
        region=Regions.JP,
        title=data["title"],
        nsuid=data.get("nsuid"),
        product_code=product_code,
    )

    game.description = data.get("text")
    game.slug = data.get("icode")
    game.free_to_play = data.get("price") == 0.0

    # Players
    players = data.get("player") or ["0"]
    game.players = max(map(int, players[0].split("~")))

    # Release Date
    try:
        game.release_date = datetime.strptime(
            data.get("sdate"),
            "%Y.%m.%d"
        )
    except (ValueError, TypeError):
        game.release_date = None

    # Categories
    game.categories = data.get("genre", [])

    # Developer
    developer = data.get("maker")
    game.developers = [developer] if developer else []

    # Languages
    game.languages = data.get("lang", [])

    # Publisher
    publisher = data.get("publisher")
    game.publishers = [publisher] if publisher else []

    # Rating (CERO)
    rating = data.get("cero") or ["0"]
    game.rating = (Ratings.CERO, RATINGS.get(rating[0]))

    # Features
    game.features = {
        Features.AMIIBO: data.get("amiibo", "0") == "1",
    }

    if game.platform == Platforms.NINTENDO_SWITCH:
        game.features[Features.DLC] = len(data.get("cnsuid") or []) > 0
        game.features[Features.NSO_REQUIRED] = (data.get("nso") or ["0"]) == ["1"]

    return game
