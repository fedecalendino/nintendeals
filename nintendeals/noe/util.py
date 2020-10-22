from datetime import datetime
from typing import Dict

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Features, Platforms, Ratings, Regions

PLATFORMS = {
    "Wii U": Platforms.NINTENDO_WIIU,
    "Nintendo 3DS": Platforms.NINTENDO_3DS,
    "New Nintendo 3DS": Platforms.NINTENDO_3DS,
    "Nintendo Switch": Platforms.NINTENDO_SWITCH,
}


def build_game(data: Dict) -> Game:
    nsuid = data.get("nsuid_txt", [None])[0]
    product_code = data.get("product_code_txt", [None])[0]
    system_name = [sm for sm in data["system_names_txt"] if sm in PLATFORMS][0]

    game = Game(
        platform=PLATFORMS[system_name],
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
    game.languages = languages[0].split(",") if languages else []

    # Publisher
    publisher = data.get("publisher")
    game.publishers = [publisher] if publisher else []

    # Rating (PEGI)
    game.rating = (Ratings.PEGI, data.get("age_rating_sorting_i"))

    # Features
    game.features = {
        Features.AMIIBO: data.get("near_field_comm_b", False),
        Features.DEMO: data.get("demo_availability", False),
        Features.DLC: data.get("dlc_shown_b", False),
        Features.LOCAL_MULTIPLAYER: data.get("local_play", False),
        Features.NSO_REQUIRED: data.get("paid_subscription_required_b", False),
        Features.SAVE_DATA_CLOUD: data.get("cloud_saves_b", False),
        Features.GAME_VOUCHERS: data.get("switch_game_voucher_b", False),
        Features.VOICE_CHAT: data.get("voice_chat_b", False),
    }

    return game
