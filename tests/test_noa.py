from nintendeals import noa
from nintendeals.classes import N3dsGame, SwitchGame
from unittest import TestCase
from datetime import datetime

LIST_LIMIT = 20


class TestNoa(TestCase):

    def test_game_info_non_existant(self):
        game = noa.game_info(nsuid="60010000000000")
        self.assertIsNone(game)

    def test_game_info_n3ds(self):
        game: N3dsGame = noa.game_info(nsuid="50010000023235")

        self.assertEqual("Super Smash Bros.", game.title)
        self.assertEqual("super-smash-bros-for-nintendo-3ds", game.na_slug)

        self.assertEqual("50010000023235", game.nsuid)
        self.assertEqual("AXC", game.unique_id)

        self.assertEqual("Sora Ltd.", game.developer)
        self.assertEqual("Nintendo", game.publisher)

        self.assertEqual("NA", game.region)
        self.assertEqual("Nintendo 3DS", game.platform)

        self.assertEqual(2014, game.release_date.year)
        self.assertEqual(10, game.release_date.month)
        self.assertEqual(3, game.release_date.day)

        self.assertIn(
            "Super Smash Bros. for Nintendo 3DS is the first portable entry",
            game.description,
        )

        self.assertEqual(["Action"], game.genres)
        self.assertEqual(4, game.players)
        self.assertEqual(1137, game.size)

        self.assertIsNone(game.amiibo)
        self.assertTrue(game.demo)
        self.assertIsNone(game.dlc)
        self.assertFalse(game.free_to_play)

        self.assertFalse(game.street_pass)
        self.assertFalse(game.virtual_console)

    def test_game_info_switch(self):
        game: SwitchGame = noa.game_info(nsuid="70010000012332")

        self.assertEqual("Super Smash Bros.™ Ultimate", game.title)
        self.assertEqual("super-smash-bros-ultimate-switch", game.na_slug)

        self.assertEqual("70010000012332", game.nsuid)
        self.assertEqual("AAAB", game.unique_id)

        self.assertEqual("NA", game.region)
        self.assertEqual("Nintendo Switch", game.platform)

        self.assertEqual(2018, game.release_date.year)
        self.assertEqual(12, game.release_date.month)
        self.assertEqual(7, game.release_date.day)

        self.assertIn(
            "Gaming icons clash in the ultimate brawl you can play anytime, anywhere!",
            game.description
        )

        self.assertEqual(["Action", "Fighting", "Multiplayer"], game.genres)
        self.assertEqual(
            [
                "Chinese", "Dutch", "English", "French", "German",
                "Italian", "Japanese", "Korean", "Russian", "Spanish",
            ],
            game.languages
        )
        self.assertEqual(0, game.players)
        self.assertEqual(13926, game.size)

        self.assertIsNone(game.amiibo)
        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)

        self.assertIsNone(game.game_vouchers)
        self.assertIsNone(game.local_multiplayer)
        self.assertTrue(game.nso_required)
        self.assertTrue(game.save_data_cloud)

    def test_list_n3ds_games(self):
        for index, game in enumerate(noa.list_3ds_games()):
            if index > LIST_LIMIT:
                break

            self.assertIsNotNone(game.title)
            self.assertIsNotNone(game.na_slug)
            self.assertIsNotNone(game.description)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("5001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 3)

    def test_list_switch_games(self):
        for index, game in enumerate(noa.list_switch_games()):
            if index > LIST_LIMIT:
                break

            self.assertIsNotNone(game.title)
            self.assertIsNotNone(game.na_slug)
            self.assertIsNotNone(game.description)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("7001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 4)

    def test_search_n3ds_games(self):
        search = noa.search_3ds_games(
            title="Zelda",
            released_after=datetime(2015, 1, 1),
            released_before=datetime(2017, 12, 31)
        )

        index = 0

        # ALttP, MM, TH
        for index, game in enumerate(search, start=1):
            self.assertIn("Zelda", game.title)
            self.assertIsNotNone(game.na_slug)
            self.assertIsNotNone(game.description)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("5001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 3)

        self.assertEqual(3, index)

    def test_search_switch_games(self):
        search = noa.search_switch_games(
            title="Zelda",
            released_at=datetime(2017, 3, 3),
        )

        game = next(search)

        self.assertEqual("The Legend of Zelda: Breath of the Wild", game.title)
        self.assertEqual("70010000000025", game.nsuid)
        self.assertEqual("the-legend-of-zelda-breath-of-the-wild-switch", game.na_slug)
        self.assertIsNotNone(game.description)

        self.assertEqual("Nintendo", game.developer)
        self.assertFalse(game.free_to_play)

        self.assertEqual(
            ["Action", "Adventure", "Other", "Role-Playing"],
            game.genres
        )
