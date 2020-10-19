from datetime import datetime
from unittest import TestCase

from nintendeals import noa
from nintendeals.classes import SwitchGame

LIST_LIMIT = 20


class TestNoa(TestCase):

    def test_game_info_non_existant(self):
        game = noa.game_info(nsuid="60010000000000")
        self.assertIsNone(game)

    def test_game_info_switch(self):
        game: SwitchGame = noa.game_info(nsuid="70010000012332")

        self.assertEqual("Super Smash Bros.™ Ultimate", game.title)
        self.assertEqual("super-smash-bros-ultimate-switch", game.slug)

        self.assertEqual("70010000012332", game.nsuid)
        self.assertEqual("AAAB", game.unique_id)

        self.assertEqual("NA", game.region)
        self.assertEqual("Nintendo Switch", game.platform)
        self.assertEqual("ESRB: Everyone 10+", game.rating)

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
        self.assertEqual(8, game.players)

        self.assertIsNone(game.amiibo)
        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)

        self.assertIsNone(game.local_multiplayer)
        self.assertTrue(game.nso_required)
        self.assertTrue(game.save_data_cloud)

    def test_list_switch_games(self):
        for index, game in enumerate(noa.list_switch_games()):
            if index > LIST_LIMIT:
                break

            self.assertIsNotNone(game.title)
            self.assertIsNotNone(game.slug)
            self.assertIsNotNone(game.description)

            self.assertEqual("NA", game.region)
            self.assertEqual("Nintendo Switch", game.platform)

            if game.rating:
                self.assertIn("ESRB", game.rating)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("7001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 4)

    def test_search_switch_games(self):
        search = noa.search_switch_games(
            title="Zelda",
            released_at=datetime(2017, 3, 3),
        )

        game = next(search)

        self.assertEqual("The Legend of Zelda™: Breath of the Wild", game.title)
        self.assertEqual("70010000000025", game.nsuid)
        self.assertEqual("the-legend-of-zelda-breath-of-the-wild-switch", game.slug)
        self.assertIsNotNone(game.description)

        self.assertEqual("Nintendo", game.developer)
        self.assertFalse(game.free_to_play)

        self.assertEqual(
            ["Action", "Adventure", "Other", "Role-Playing"],
            game.genres
        )
