from unittest import TestCase

from nintendeals import noj


class TestNoJ(TestCase):

    def test_tloz_botw(self):
        nsuid = "70010000000026"
        game = noj.game_info(nsuid)

        self.assertEqual(game.title, "ゼルダの伝説　ブレス オブ ザ ワイルド")
        self.assertEqual(game.product_code, "HACAAAAA")
        self.assertEqual(game.publisher, "任天堂")
        self.assertEqual(game.players, 1)

        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)
        self.assertFalse(game.online_play)
        self.assertTrue(game.save_data_cloud)

    def test_splatoon_2(self):
        nsuid = "70010000000309"
        game = noj.game_info(nsuid)

        self.assertEqual(game.title, "スプラトゥーン2")
        self.assertEqual(game.product_code, "HACAAB6A")
        self.assertEqual(game.publisher, "任天堂")
        self.assertEqual(game.players, 8)

        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)
        self.assertFalse(game.save_data_cloud)
        self.assertTrue(game.online_play)

    def test_arms(self):
        nsuid = "70010000000308"
        game = noj.game_info(nsuid)

        self.assertEqual(game.title, "ARMS")
        self.assertEqual(game.product_code, "HACAABQA")
        self.assertEqual(game.publisher, "任天堂")
        self.assertEqual(game.players, 4)

        self.assertTrue(game.demo)
        self.assertFalse(game.dlc)
        self.assertFalse(game.free_to_play)
        self.assertTrue(game.online_play)
        self.assertTrue(game.save_data_cloud)

    def test_pokemon_quest(self):
        nsuid = "70010000003483"
        game = noj.game_info(nsuid)

        self.assertEqual(game.title, "ポケモンクエスト")
        self.assertEqual(game.product_code, "HACAK35A")
        self.assertEqual(game.publisher, "ポケモン")
        self.assertEqual(game.players, 1)

        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertTrue(game.free_to_play)
        self.assertFalse(game.online_play)
        self.assertTrue(game.save_data_cloud)
