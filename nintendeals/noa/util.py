from datetime import datetime
from typing import Dict

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Features, Platforms, Ratings, Regions

PLATFORMS = {
    "Nintendo Switch": Platforms.NINTENDO_SWITCH,
    "Nintendo Switch – OLED Model": Platforms.NINTENDO_SWITCH
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
    game.slug = data.get("urlKey")
    game.free_to_play = data.get("priceRange") == "Free to start"

    # Players
    game.players = extra.get("players") or 1

    # Release Date
    try:
        release_date = data["releaseDate"].split("T")[0]
        game.release_date = datetime.strptime(release_date, "%Y-%m-%d")
    except (AttributeError, KeyError, ValueError):
        game.release_date = None

    # Categories
    game.categories = data.get("genres", [])

    # Developer
    developer = data.get("softwareDeveloper")
    game.developers = [developer] if developer else []

    # Languages
    game.languages = extra.get("languages", [])

    # Publisher
    publisher = data.get("softwarePublisher")
    game.publishers = [publisher] if publisher else []

    # Rating (ESRB)
    game.rating = (Ratings.ESRB, data.get("esrbRating"))

    # Features
    filters = list(map(str.lower, data.get("topLevelFilters") or []))
    nso_features = list(map(str.lower, data.get("nsoFeatures") or []))

    game.features = {
        Features.DEMO: "demo available" in filters,
        Features.GAME_VOUCHER: "game voucher eligible" in filters,
        Features.DLC: extra.get("dlc", False) if extra else None,
        Features.ONLINE_PLAY: "online play" in nso_features,
        Features.SAVE_DATA_CLOUD: "save data cloud" in nso_features,
    }

    return game
