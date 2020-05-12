from datetime import datetime
from unittest import TestCase

from nintendeals import noe
from nintendeals.classes import N3dsGame, SwitchGame

LIST_LIMIT = 20


class TestNoe(TestCase):

    def test_game_info_non_existant(self):
        game = noe.game_info(nsuid="60010000000000")
        self.assertIsNone(game)

    def test_game_info_n3ds(self):
        game: N3dsGame = noe.game_info(nsuid="50010000024975")

        self.assertEqual("Super Smash Bros. for Nintendo 3DS", game.title)
        self.assertEqual(
            "/Games/Nintendo-3DS/Super-Smash-Bros-for-Nintendo-3DS-864329.html",
            game.slug
        )

        self.assertEqual("50010000024975", game.nsuid)
        self.assertEqual("AXC", game.unique_id)

        self.assertEqual("Nintendo", game.publisher)

        self.assertEqual("EU", game.region)
        self.assertEqual("Nintendo 3DS", game.platform)

        self.assertEqual(2014, game.release_date.year)
        self.assertEqual(10, game.release_date.month)
        self.assertEqual(3, game.release_date.day)

        # self.assertIn(
        #   "Super Smash Bros. for Nintendo 3DS is truly a clash for the ages!",
        #   game.description,
        # )

        self.assertEqual(["Action", "Fighting"], game.genres)
        self.assertEqual(4, game.players)
        self.assertEqual(1371, game.size)

        self.assertTrue(game.amiibo)
        self.assertTrue(game.demo)
        self.assertFalse(game.dlc)
        self.assertFalse(game.free_to_play)

        self.assertTrue(game.street_pass)
        self.assertFalse(game.virtual_console)

    def test_game_info_switch(self):
        game: SwitchGame = noe.game_info(nsuid="70010000012331")

        self.assertEqual("Super Smash Bros. Ultimate", game.title)
        self.assertEqual(
            "/Games/Nintendo-Switch/Super-Smash-Bros-Ultimate-1395713.html",
            game.slug
        )

        self.assertEqual("70010000012331", game.nsuid)
        self.assertEqual("AAAB", game.unique_id)

        self.assertEqual("EU", game.region)
        self.assertEqual("Nintendo Switch", game.platform)

        self.assertEqual("Nintendo / Sora Ltd. / BANDAI NAMCO Studios Inc.", game.developer)
        self.assertEqual("Nintendo", game.publisher)

        self.assertEqual(2018, game.release_date.year)
        self.assertEqual(12, game.release_date.month)
        self.assertEqual(7, game.release_date.day)

        self.assertIn(
            "a new entry in the Super Smash Bros. series for Nintendo Switch!",
            game.description
        )

        self.assertEqual(["Action", "Fighting"], game.genres)
        self.assertEqual(
            [
                "Chinese", "Dutch", "English", "French", "German",
                "Italian", "Japanese", "Korean", "Russian", "Spanish"
            ],
            game.languages
        )

        self.assertEqual(8, game.players)
        self.assertEqual(15869, game.size)

        self.assertTrue(game.amiibo)
        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)

        self.assertFalse(game.game_vouchers)
        self.assertFalse(game.local_multiplayer)
        self.assertTrue(game.nso_required)
        self.assertTrue(game.save_data_cloud)

    def test_list_n3ds_games(self):
        for index, game in enumerate(noe.list_3ds_games()):
            if index > LIST_LIMIT:
                break

            self.assertIsNotNone(game.title)
            self.assertIsNotNone(game.slug)

            self.assertEqual("EU", game.region)
            self.assertEqual("Nintendo 3DS", game.platform)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("5001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 3)

    def test_list_switch_games(self):
        for index, game in enumerate(noe.list_switch_games()):
            if index > LIST_LIMIT:
                break

            self.assertIsNotNone(game.title)
            self.assertIsNotNone(game.slug)

            self.assertEqual("EU", game.region)
            self.assertEqual("Nintendo Switch", game.platform)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("7001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 4)

    def test_search_n3ds_games(self):
        search = noe.search_3ds_games(
            title="Zelda",
            released_after=datetime(2015, 1, 1),
            released_before=datetime(2017, 12, 31)
        )

        index = 0

        # MM, TFH
        for index, game in enumerate(search, start=1):
            self.assertIn("Zelda", game.title)
            self.assertIsNotNone(game.slug)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("5001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 3)

        self.assertEqual(2, index)

    def test_search_switch_games(self):
        search = noe.search_switch_games(
            title="Zelda",
            released_at=datetime(2017, 3, 3),
        )

        game = next(search)

        self.assertEqual("The Legend of Zelda: Breath of the Wild", game.title)
        self.assertEqual("70010000000023", game.nsuid)
        self.assertEqual(
            "/Games/Nintendo-Switch/The-Legend-of-Zelda-Breath-of-the-Wild-1173609.html",
            game.slug
        )

        self.assertEqual("Nintendo", game.developer)
        self.assertFalse(game.free_to_play)

        self.assertEqual(['Action', 'Adventure'], game.genres)
