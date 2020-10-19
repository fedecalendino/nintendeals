import logging
from datetime import datetime
from typing import Iterator, Type

from nintendeals.classes import SwitchGame
from nintendeals.constants import EU, SWITCH
from nintendeals.noe.api.nintendo import search

log = logging.getLogger(__name__)


def _list_games(
    game_class: Type,
    platform: str,
    **kwargs
) -> Iterator[SwitchGame]:
    for data in search(platform):
        product_codes = [
            pc for pc in data.get("product_code_txt", [])
            if "-" not in pc
        ] or [None]

        nsuids = list(reversed(sorted(data.get("nsuid_txt", [None]))))

        game = game_class(
            region=EU,
            title=data["title_extras_txt"][0],
            nsuid=nsuids[0],
            product_code=product_codes[0],
        )

        game.slug = data.get("url")

        game.description = data.get("excerpt")
        game.developer = data.get("developer")
        game.publisher = data.get("publisher")
        game.genres = data.get("pretty_game_categories_txt", [])
        game.players = data.get("players_to")
        game.languages = list(sorted(map(
            lambda lang: lang.title(),
            data.get("language_availability", [""])[0].split(",")
        )))

        rating = data.get("age_rating_sorting_i")

        if rating:
            game.rating = f"PEGI: {rating}"

        try:
            game.release_date = datetime.strptime(
                data["dates_released_dts"][0].split("T")[0],
                '%Y-%m-%d'
            )
        except (ValueError, TypeError):
            game.release_date = None

        if "datasize_readable_txt" in data:
            value, unit = data.get("datasize_readable_txt", [""])[0].split()

            if unit.lower() == "blocks":
                value = int(value) // 8
        else:
            value = None

        game.megabytes = value

        banner_img = data.get("wishlist_email_banner640w_image_url_s")
        game.banner_img = ("https:" + banner_img) if banner_img else None

        cover_img = data.get("image_url_sq_s")
        game.cover_img = ("https:" + cover_img) if cover_img else None

        # Features
        game.amiibo = data.get("near_field_comm_b", False)
        game.demo = data.get("demo_availability", False)
        game.dlc = data.get("dlc_shown_b", False)
        game.free_to_play = data.get("price_regular_f") == 0.0

        if game.platform == SWITCH:
            game.local_multiplayer = data.get("local_play", False)
            game.nso_required = data.get("paid_subscription_required_b", False)
            game.save_data_cloud = data.get("cloud_saves_b", False)
            game.game_vouchers = data.get("switch_game_voucher_b", False)
            game.voice_chat = data.get("voice_chat_b", False)

        yield game


def list_switch_games(**kwargs) -> Iterator[SwitchGame]:
    """
        List all the Switch games in Nintendo of Europe. The following subset
    of data will be available for each game.

    Game data
    ---------
        * platform: str ["Nintendo Switch"]
        * region: str ["EU"]
        * title: str
        * nsuid: str (optional)
        * product_code: str (optional)

        * slug: str

        * amiibo: bool
        * demo: bool
        * developer: str
        * dlc: bool
        * free_to_play: bool
        * game_vouchers: bool
        * genres: List[str]
        * languages: List[str]
        * local_multiplayer: bool
        * nso_required: bool
        * players: int
        * publisher: str
        * rating: str (PEGI)
        * release_date: datetime
        * save_data_cloud: bool
        * voice_chat: bool

        * banner_img: str
        * cover_img: str

    Yields
    -------
    nintendeals.classes.SwitchGame:
        Switch game from Nintendo of Europe.
    """
    log.info("Fetching list of Nintendo Switch games")

    yield from _list_games(
        game_class=SwitchGame,
        platform="Switch",
        **kwargs
    )
