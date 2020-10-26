from datetime import datetime
from typing import Dict

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Features, Platforms, Ratings, Regions

NSUIDS = {
    "500": Platforms.NINTENDO_3DS,
    "700": Platforms.NINTENDO_SWITCH,
    "200": Platforms.NINTENDO_WIIU,
}

PLATFORMS = {
    "CTR": Platforms.NINTENDO_3DS,
    "KTR": Platforms.NINTENDO_3DS,
    "HAC": Platforms.NINTENDO_SWITCH,
    "WUP": Platforms.NINTENDO_WIIU,
}


def build_game(data: Dict) -> Game:
    nsuid = data.get("nsuid_txt")
    product_code = data.get("product_code_txt")

    if nsuid:
        platform = NSUIDS[nsuid[:3]]
    else:
        platform = PLATFORMS[product_code[:3]]

    game = Game(
        platform=platform,
        region=Regions.EU,
        title=data["title"],
        nsuid=nsuid,
        product_code=product_code,
    )

    game.description = data.get("excerpt")
    game.slug = data.get("url")
    game.players = data.get("players_to", 0)
    game.free_to_play = data.get("price_regular_f") == 0.0

    # Release Date
    try:
        game.release_date = datetime.strptime(
            data.get("pretty_date_s"),
            "%d/%m/%Y"
        )
    except (ValueError, TypeError):
        game.release_date = None

    # Categories
    game.categories = data.get("game_categories_txt", [])

    # Developer
    developer = data.get("developer")
    game.developers = [developer] if developer else []

    # Languages
    languages = data.get("language_availability")
    game.languages = list(map(str.title, languages[0].split(","))) if languages else []

    # Publisher
    publisher = data.get("publisher")
    game.publishers = [publisher] if publisher else []

    # Rating (PEGI)
    game.rating = (Ratings.PEGI, data.get("age_rating_sorting_i"))

    # Features
    game.features = {
        Features.AMIIBO: data.get("near_field_comm_b", False),
        Features.DEMO: data.get("demo_availability", False),
        Features.DLC: data.get("add_on_content_b", False),
    }

    if game.platform == Platforms.NINTENDO_SWITCH:
        game.features[Features.NSO_REQUIRED] = data.get("paid_subscription_required_b", False)
        game.features[Features.SAVE_DATA_CLOUD] = data.get("cloud_saves_b", False)
        game.features[Features.VOICE_CHAT] = data.get("voice_chat_b", False)

    return game
