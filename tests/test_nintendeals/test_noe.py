from unittest import TestCase

from nintendeals import noe


class TestNoE(TestCase):

    def test_tloz_botw(self):
        nsuid = "70010000000023"
        game = noe.game_info(nsuid)

        self.assertEqual(game.title, "The Legend of Zelda: Breath of the Wild")
        self.assertEqual(game.product_code, "HACPAAAAA")
        self.assertEqual(game.publisher, "Nintendo")
        self.assertEqual(game.players, 1)

        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)
        self.assertFalse(game.online_play)
        self.assertTrue(game.save_data_cloud)

    def test_splatoon_2(self):
        nsuid = "70010000000151"
        game = noe.game_info(nsuid)

        self.assertEqual(game.title, "Splatoon 2")
        self.assertEqual(game.product_code, "HACPAAB6C")
        self.assertEqual(game.players, 8)

        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)
        self.assertFalse(game.save_data_cloud)
        self.assertTrue(game.online_play)

    def test_arms(self):
        nsuid = "70010000000152"
        game = noe.game_info(nsuid)

        self.assertEqual(game.title, "ARMS")
        self.assertEqual(game.product_code, "HACPAABQA")
        self.assertEqual(game.publisher, "Nintendo")
        self.assertEqual(game.players, 4)

        self.assertTrue(game.demo)
        self.assertFalse(game.dlc)
        self.assertFalse(game.free_to_play)
        self.assertTrue(game.online_play)
        self.assertTrue(game.save_data_cloud)

    def test_pokemon_quest(self):
        nsuid = "70010000003481"
        game = noe.game_info(nsuid)

        self.assertEqual(game.title, "Pokémon Quest")
        self.assertEqual(game.product_code, "HACPAK35A")
        self.assertEqual(game.publisher, "Nintendo")
        self.assertEqual(game.players, 1)

        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertTrue(game.free_to_play)
        self.assertFalse(game.online_play)
        self.assertTrue(game.save_data_cloud)
