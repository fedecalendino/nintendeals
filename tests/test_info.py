import ddt
from unittest import TestCase

from nintendeals import noa, noe, noj


@ddt.ddt
class TestDetails(TestCase):

    def _assert_botw_props(self, game):
        self.assertEqual("AAAA", game.unique_id)

        self.assertEqual("Nintendo Switch", game.platform)
        self.assertEqual(2017, game.release_date.year)
        self.assertEqual(3, game.release_date.month)

        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)
        self.assertFalse(game.online_play)
        self.assertTrue(game.save_data_cloud)

        self.assertEqual(1, game.players)

        self.assertGreater(15000, game.size)
        self.assertLess(13000, game.size)

        if game.publisher is not None:
            self.assertIn(game.publisher, ["Nintendo", "任天堂"])

        if game.developer is not None:
            self.assertIn(game.developer, ["Nintendo", "任天堂"])

        if game.amiibo is not None:
            self.assertTrue(game.amiibo)

        if game.game_vouchers is not None:
            self.assertTrue(game.game_vouchers)

    def _assert_lets_go_eevee_props(self, game):
        self.assertEqual("ADW3", game.unique_id)

        self.assertEqual("Nintendo Switch", game.platform)
        self.assertEqual(2018, game.release_date.year)
        self.assertEqual(11, game.release_date.month)

        self.assertTrue(game.demo)
        self.assertFalse(game.dlc)
        self.assertFalse(game.free_to_play)
        self.assertTrue(game.online_play)
        self.assertFalse(game.save_data_cloud)

        self.assertEqual(2, game.players)

        self.assertGreater(6500, game.size)
        self.assertLess(2000, game.size)

        if game.publisher is not None:
            self.assertIn(game.publisher, ["Nintendo", "ポケモン"])

        if game.developer is not None:
            self.assertIn(game.developer, ["GAME FREAK Inc.", "GAME FREAK", "ポケモン"])

        if game.amiibo is not None:
            self.assertFalse(game.amiibo)

        if game.game_vouchers is not None:
            self.assertTrue(game.game_vouchers)

    def _assert_dead_cells_props(self, game):
        self.assertEqual("ANXT", game.unique_id)

        self.assertEqual("Nintendo Switch", game.platform)
        self.assertEqual(2018, game.release_date.year)
        self.assertEqual(8, game.release_date.month)

        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertFalse(game.free_to_play)
        self.assertFalse(game.online_play)
        self.assertTrue(game.save_data_cloud)

        self.assertEqual(1, game.players)

        self.assertGreater(1000, game.size)
        self.assertLess(400, game.size)

        if game.publisher:
            self.assertIn(game.publisher, ["Motion Twin"])

        if game.developer:
            self.assertIn(game.developer, ["Motion Twin"])

        if game.amiibo is not None:
            self.assertFalse(game.amiibo)

        if game.game_vouchers is not None:
            self.assertFalse(game.game_vouchers)

    def _assert_pokemon_quest_props(self, game):
        self.assertEqual("AK35", game.unique_id)

        self.assertEqual("Nintendo Switch", game.platform)
        self.assertEqual(2018, game.release_date.year)
        self.assertEqual(5, game.release_date.month)

        self.assertFalse(game.demo)
        self.assertTrue(game.dlc)
        self.assertTrue(game.free_to_play)
        self.assertFalse(game.online_play)
        self.assertTrue(game.save_data_cloud)

        self.assertEqual(1, game.players)

        self.assertGreater(500, game.size)
        self.assertLess(100, game.size)

        if game.publisher:
            self.assertIn(game.publisher, ["Nintendo", "ポケモン"])

        if game.developer:
            self.assertIn(game.developer, ["GAME FREAK inc.", "ポケモン"])

        if game.amiibo is not None:
            self.assertFalse(game.amiibo)

        if game.game_vouchers is not None:
            self.assertFalse(game.game_vouchers)

    @ddt.data(
        ("70010000000025", "The Legend of Zelda™: Breath of the Wild", _assert_botw_props),
        ("70010000000450", "Pokémon™: Let’s Go, Eevee!", _assert_lets_go_eevee_props),
        ("70010000003482", "Pokémon™ Quest", _assert_pokemon_quest_props),
        ("70010000007706", "Dead Cells", _assert_dead_cells_props),
    )
    @ddt.unpack
    def test_noa(self, nsuid, title, checker):
        nintendo = noa

        game = nintendo.game_info(nsuid)
        self.assertEqual(title, game.title)
        checker(self, game)

    @ddt.data(
        ("70010000000023", "The Legend of Zelda: Breath of the Wild", _assert_botw_props),
        ("70010000000449", "Pokémon: Let's Go, Eevee!", _assert_lets_go_eevee_props),
        ("70010000003481", "Pokémon Quest", _assert_pokemon_quest_props),
        ("70010000007705", "Dead Cells", _assert_dead_cells_props),
    )
    @ddt.unpack
    def test_noe(self, nsuid, title, checker):
        nintendo = noe

        game = nintendo.game_info(nsuid)
        self.assertEqual(title, game.title)
        checker(self, game)

    @ddt.data(
        ("70010000000026", "ゼルダの伝説　ブレス オブ ザ ワイルド", _assert_botw_props),
        ("70010000000451", "ポケットモンスター Let's Go! イーブイ", _assert_lets_go_eevee_props),
        ("70010000003483", "ポケモンクエスト", _assert_pokemon_quest_props),
        ("70010000013175", "Dead Cells", _assert_dead_cells_props),
    )
    @ddt.unpack
    def test_noj(self, nsuid, title, checker):
        nintendo = noj

        game = nintendo.game_info(nsuid)
        self.assertEqual(title, game.title)
        checker(self, game)
