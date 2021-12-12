from unittest import TestCase

from nintendeals import noe
from nintendeals.commons.enumerates import Features, Ratings, Regions, Platforms


class TestGameInfo(TestCase):

    def test_game_info_non_existant(self):
        game = noe.game_info("60010000000000")
        self.assertIsNone(game)

    def test_game_info_3ds(self):
        game = noe.game_info("50010000024975")

        self.assertEqual(game.platform, Platforms.NINTENDO_3DS)
        self.assertEqual(game.region, Regions.EU)
        self.assertEqual(game.title, "Super Smash Bros. for Nintendo 3DS")
        self.assertEqual(game.nsuid, "50010000024975")
        self.assertEqual(game.unique_id, "AXC")

        self.assertEqual(game.slug, "/Games/Nintendo-3DS-games/Super-Smash-Bros-for-Nintendo-3DS-864329.html")

        self.assertEqual(game.players, 4)
        self.assertFalse(game.free_to_play)

        self.assertEqual(game.rating, (Ratings.PEGI, 12))

        self.assertEqual(game.release_date.year, 2014)
        self.assertEqual(game.release_date.month, 10)
        self.assertEqual(game.release_date.day, 3)

        self.assertIn("Nintendo", game.publishers)

        self.assertEqual(game.features.get(Features.AMIIBO), True)
        self.assertEqual(game.features.get(Features.DEMO), True)
        self.assertEqual(game.features.get(Features.DLC), True)

        self.assertEqual(game.eshop.at_de, "https://www.nintendo.at/Games/Nintendo-3DS-games/Super-Smash-Bros-for-Nintendo-3DS-864329.html")
        self.assertEqual(game.eshop.be_fr, "https://www.nintendo.be/fr/Games/Nintendo-3DS-games/Super-Smash-Bros-for-Nintendo-3DS-864329.html")
        self.assertEqual(game.eshop.be_nl, "https://www.nintendo.be/nl/Games/Nintendo-3DS-games/Super-Smash-Bros-for-Nintendo-3DS-864329.html")
        self.assertEqual(game.eshop.ch_de, "https://www.nintendo.ch/de/Games/Nintendo-3DS-games/Super-Smash-Bros-for-Nintendo-3DS-864329.html")
        self.assertEqual(game.eshop.ch_fr, "https://www.nintendo.ch/fr/Games/Nintendo-3DS-games/Super-Smash-Bros-for-Nintendo-3DS-864329.html")
        self.assertEqual(game.eshop.ch_it, "https://www.nintendo.ch/it/Games/Nintendo-3DS-games/Super-Smash-Bros-for-Nintendo-3DS-864329.html")

    def test_game_info_switch(self):
        game = noe.game_info("70010000012331")

        self.assertEqual(game.platform, Platforms.NINTENDO_SWITCH)
        self.assertEqual(game.region, Regions.EU)
        self.assertEqual(game.title, "Super Smash Bros. Ultimate")
        self.assertEqual(game.nsuid, "70010000012331")
        self.assertEqual(game.unique_id, "AAAB")

        self.assertEqual(game.slug, "/Games/Nintendo-Switch-games/Super-Smash-Bros-Ultimate-1395713.html")

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
        self.assertEqual(game.features.get(Features.NSO_REQUIRED), True)
        self.assertEqual(game.features.get(Features.SAVE_DATA_CLOUD), True)
        self.assertEqual(game.features.get(Features.VOICE_CHAT), True)

        self.assertEqual(game.eshop.ru_ru, "https://www.nintendo.ru/-/Games/Nintendo-Switch-games/Super-Smash-Bros-Ultimate-1395713.html")
        self.assertEqual(game.eshop.uk_en, "https://www.nintendo.co.uk/Games/Nintendo-Switch-games/Super-Smash-Bros-Ultimate-1395713.html")
        self.assertEqual(game.eshop.za_en, "https://www.nintendo.co.za/Games/Nintendo-Switch-games/Super-Smash-Bros-Ultimate-1395713.html")
        self.assertEqual(game.eshop.au_en, "https://ec.nintendo.com/AU/en/titles/70010000012331")
        self.assertEqual(game.eshop.nz_en, "https://ec.nintendo.com/NZ/en/titles/70010000012331")

    def test_game_info_wiiu(self):
        game = noe.game_info("20010000010926")

        self.assertEqual(game.platform, Platforms.NINTENDO_WIIU)
        self.assertEqual(game.region, Regions.EU)
        self.assertEqual(game.title, "Super Smash Bros. for Wii U")
        self.assertEqual(game.nsuid, "20010000010926")
        self.assertEqual(game.unique_id, "AXF")

        self.assertEqual(game.slug, "/Games/Wii-U-games/Super-Smash-Bros-for-Wii-U-864849.html")

        self.assertEqual(game.players, 8)
        self.assertFalse(game.free_to_play)

        self.assertEqual(game.rating, (Ratings.PEGI, 12))

        self.assertEqual(game.release_date.year, 2014)
        self.assertEqual(game.release_date.month, 11)
        self.assertEqual(game.release_date.day, 28)

        self.assertIn("Nintendo", game.publishers)

        self.assertEqual(game.features.get(Features.AMIIBO), True)
        self.assertEqual(game.features.get(Features.DEMO), False)
        self.assertEqual(game.features.get(Features.DLC), True)

        self.assertEqual(game.eshop.de_de, "https://www.nintendo.de/Games/Wii-U-games/Super-Smash-Bros-for-Wii-U-864849.html")
        self.assertEqual(game.eshop.es_es, "https://www.nintendo.es/Games/Wii-U-games/Super-Smash-Bros-for-Wii-U-864849.html")
        self.assertEqual(game.eshop.fr_fr, "https://www.nintendo.fr/Games/Wii-U-games/Super-Smash-Bros-for-Wii-U-864849.html")
        self.assertEqual(game.eshop.it_it, "https://www.nintendo.it/Games/Wii-U-games/Super-Smash-Bros-for-Wii-U-864849.html")
        self.assertEqual(game.eshop.nl_nl, "https://www.nintendo.nl/Games/Wii-U-games/Super-Smash-Bros-for-Wii-U-864849.html")
        self.assertEqual(game.eshop.pt_pt, "https://www.nintendo.pt/Games/Wii-U-games/Super-Smash-Bros-for-Wii-U-864849.html")
