import re
from datetime import datetime
from typing import Dict

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Features, Platforms, Ratings, Regions

PLATFORMS = {
    "Nintendo Switch": Platforms.NINTENDO_SWITCH,
}


def build_game(data: Dict) -> Game:
    extra = data.get("extra", {})

    game = Game(
        platform=PLATFORMS[data["platform"]],
        region=Regions.NA,
        title=data["title"],
        nsuid=data.get("nsuid"),
        product_code=extra.get("product_code"),
    )

    game.description = data.get("description")
    game.slug = data.get("slug")
    game.free_to_play = data.get("free_to_start", False)

    # Players
    try:
        game.players = int(re.sub(r"[^\d]*", "", data["numOfPlayers"]))
    except (KeyError, ValueError):
        game.players = 0

    # Release Date
    try:
        release_date = data["releaseDateDisplay"].split("T")[0]
        game.release_date = datetime.strptime(release_date, "%Y-%m-%d")
    except (KeyError, ValueError):
        game.release_date = None

    # Categories
    game.categories = data.get("genres", [])

    # Developer
    game.developers = data.get("developers", [])

    # Languages
    game.languages = extra.get("languages", [])

    # Publisher
    game.publishers = data.get("publishers", [])

    # Rating (ESRB)
    game.rating = (Ratings.ESRB, data.get("esrbRating"))

    # Features
    filters = data.get("generalFilters", [])

    game.features = {
        Features.DEMO: "Demo available" in filters,
        Features.DLC: "DLC available" in filters,
        Features.NSO_REQUIRED: "Nintendo Switch Online compatible" in filters,
        Features.SAVE_DATA_CLOUD: extra.get("save_data_cloud"),
    }

    return game
