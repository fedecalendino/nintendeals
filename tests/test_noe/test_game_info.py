from unittest import TestCase

from nintendeals import noe
from nintendeals.commons.enumerates import Features, Ratings, Regions, Platforms


class TestGameInfo(TestCase):
    def test_game_info_non_existant(self):
        game = noe.game_info("60010000000000")
        self.assertIsNone(game)

    def test_game_info_switch(self):
        game = noe.game_info("70010000012331")

        self.assertEqual(game.platform, Platforms.NINTENDO_SWITCH)
        self.assertEqual(game.region, Regions.EU)
        self.assertEqual(game.title, "Super Smash Bros. Ultimate")
        self.assertEqual(game.nsuid, "70010000012331")
        self.assertEqual(game.unique_id, "AAAB")

        self.assertEqual(
            game.slug,
            "/Games/Nintendo-Switch-games/Super-Smash-Bros-Ultimate-1395713.html",
        )

        self.assertEqual(game.players, 8)
        self.assertFalse(game.free_to_play)

        self.assertEqual(game.rating, (Ratings.PEGI, 12))

        self.assertEqual(game.release_date.year, 2018)
        self.assertEqual(game.release_date.month, 12)
        self.assertEqual(game.release_date.day, 7)

        self.assertIn("Nintendo", game.publishers)

        self.assertEqual(game.features.get(Features.AMIIBO), True)
        self.assertEqual(game.features.get(Features.DEMO), False)
        self.assertEqual(game.features.get(Features.DLC), True)
        self.assertEqual(game.features.get(Features.ONLINE_PLAY), True)
        self.assertEqual(game.features.get(Features.SAVE_DATA_CLOUD), True)
        self.assertEqual(game.features.get(Features.VOICE_CHAT), True)

        self.assertEqual(
            game.eshop.ru_ru,
            "https://www.nintendo.ru/-/Games/Nintendo-Switch-games/Super-Smash-Bros-Ultimate-1395713.html",
        )
        self.assertEqual(
            game.eshop.uk_en,
            "https://www.nintendo.co.uk/Games/Nintendo-Switch-games/Super-Smash-Bros-Ultimate-1395713.html",
        )
        self.assertEqual(
            game.eshop.za_en,
            "https://www.nintendo.co.za/Games/Nintendo-Switch-games/Super-Smash-Bros-Ultimate-1395713.html",
        )
        self.assertEqual(game.eshop.au_en, "https://ec.nintendo.com/AU/en/titles/70010000012331")
        self.assertEqual(game.eshop.nz_en, "https://ec.nintendo.com/NZ/en/titles/70010000012331")
