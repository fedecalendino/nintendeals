from datetime import datetime
from unittest import TestCase

from nintendeals import noj
from nintendeals.classes import N3dsGame, SwitchGame

LIST_LIMIT = 20


class TestNoj(TestCase):

    def test_game_info_non_existant(self):
        game = noj.game_info(nsuid="60010000000000")
        self.assertIsNone(game)

    def test_game_info_n3ds(self):
        game: N3dsGame = noj.game_info(nsuid="50010000025416")

        self.assertEqual("大乱闘スマッシュブラザーズ for Nintendo 3DS", game.title)

        self.assertEqual("50010000025416", game.nsuid)
        self.assertEqual("AXC", game.unique_id)

        self.assertEqual("JP", game.region)
        self.assertEqual("Nintendo 3DS", game.platform)

        self.assertEqual(2014, game.release_date.year)
        self.assertEqual(9, game.release_date.month)
        self.assertEqual(13, game.release_date.day)

        self.assertEqual(["アクション", "格闘"], game.genres)
        self.assertEqual(1, game.players)

        self.assertTrue(game.amiibo)
        self.assertFalse(game.dlc)
        self.assertFalse(game.free_to_play)

        self.assertFalse(game.virtual_console)

    def test_game_info_switch(self):
        game: SwitchGame = noj.game_info(nsuid="70010000012085")

        self.assertEqual("大乱闘スマッシュブラザーズ SPECIAL", game.title)

        self.assertEqual("70010000012085", game.nsuid)
        self.assertEqual("AAAB", game.unique_id)

        self.assertEqual("JP", game.region)
        self.assertEqual("Nintendo Switch", game.platform)

        self.assertEqual("任天堂", game.developer)
        self.assertEqual("任天堂", game.publisher)

        self.assertEqual(2018, game.release_date.year)
        self.assertEqual(12, game.release_date.month)
        self.assertEqual(7, game.release_date.day)

        self.assertEqual(["アクション"], game.genres)
        self.assertEqual(
            [
                "イタリア語", "オランダ語", "スペイン語", "ドイツ語", "フランス語",
                "ロシア語", "中国語 (簡体字)", "中国語 (繁体字)", "日本語",
                "英語", "韓国語",
            ],
            game.languages
        )

        self.assertEqual(8, game.players)
        self.assertEqual(16410, game.megabytes)

        self.assertTrue(game.amiibo)
        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)

        self.assertTrue(game.local_multiplayer)
        self.assertTrue(game.nso_required)
        self.assertTrue(game.save_data_cloud)

    def test_list_n3ds_games(self):
        for index, game in enumerate(noj.list_3ds_games()):
            if index > LIST_LIMIT:
                break

            self.assertIsNotNone(game.title)

            self.assertEqual("JP", game.region)
            self.assertEqual("Nintendo 3DS", game.platform)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("5001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 3)

    def test_list_switch_games(self):
        for index, game in enumerate(noj.list_switch_games()):
            if index > LIST_LIMIT:
                break

            self.assertIsNotNone(game.title)

            self.assertEqual("JP", game.region)
            self.assertEqual("Nintendo Switch", game.platform)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("7001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 4)

    def test_search_n3ds_games(self):
        search = noj.search_3ds_games(
            title="ゼルダの伝説",
            released_after=datetime(2015, 1, 1),
            released_before=datetime(2017, 12, 31)
        )

        index = 0

        # MM, TFH
        for index, game in enumerate(search, start=1):
            self.assertIn("ゼルダの伝説", game.title)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("5001"))

            if game.unique_id:
                self.assertTrue(len(game.unique_id) == 3)

        self.assertEqual(3, index)

    def test_search_switch_games(self):
        search = noj.search_switch_games(
            title="ゼルダの伝説",
            released_at=datetime(2017, 3, 3),
        )

        game = next(search)

        self.assertEqual("ゼルダの伝説　ブレス オブ ザ ワイルド", game.title)
        self.assertEqual("70010000000026", game.nsuid)

        self.assertEqual("任天堂", game.developer)
        self.assertFalse(game.free_to_play)

