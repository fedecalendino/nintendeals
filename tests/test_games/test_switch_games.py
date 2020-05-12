from unittest import TestCase

from nintendeals import noa, noe, noj
from nintendeals.classes import SwitchGame


class TestSwitchGames(TestCase):

    def test_noa(self):
        game: SwitchGame = noa.game_info(nsuid="70010000006442")

        self.assertEqual("Celeste", str(game))

        self.assertEqual("70010000006442", game.nsuid)
        self.assertEqual("ACF3", game.unique_id)

        self.assertEqual("Matt Makes Games Inc.", game.developer)
        self.assertEqual("Matt Makes Games Inc.", game.publisher)

        self.assertEqual("NA", game.region)
        self.assertEqual("Nintendo Switch", game.platform)

        self.assertEqual(2018, game.release_date.year)
        self.assertEqual(1, game.release_date.month)
        self.assertEqual(25, game.release_date.day)

        self.assertEqual(2, len(game.genres))
        self.assertEqual(10, len(game.languages))
        self.assertEqual(1, game.players)

        self.assertEqual(
            "https://ec.nintendo.com/US/en/titles/70010000006442",
            game.url(country="US")
        )

        self.assertEqual(
            "https://ec.nintendo.com/CA/fr/titles/70010000006442",
            game.url(country="CA", lang="fr")
        )

        self.assertFalse(game.demo)
        self.assertFalse(game.dlc)
        self.assertFalse(game.game_vouchers)
        self.assertFalse(game.nso_required)
        self.assertTrue(game.save_data_cloud)

    def test_noe(self):
        game: SwitchGame = noe.game_info(nsuid="70010000006441")

        self.assertEqual("Celeste", str(game))

        self.assertEqual("70010000006441", game.nsuid)
        self.assertEqual("ACF3", game.unique_id)

        self.assertEqual("Matt Makes Games Inc.", game.developer)
        self.assertEqual("Matt Makes Games Inc.", game.publisher)

        self.assertEqual("EU", game.region)
        self.assertEqual("Nintendo Switch", game.platform)

        self.assertEqual(2018, game.release_date.year)
        self.assertEqual(1, game.release_date.month)
        self.assertEqual(25, game.release_date.day)

        self.assertEqual(2, len(game.genres))
        self.assertEqual(10, len(game.languages))
        self.assertEqual(1, game.players)

        self.assertEqual(
            "https://ec.nintendo.com/GB/en/titles/70010000006441",
            game.url(country="GB")
        )

        self.assertEqual(
            "https://ec.nintendo.com/IT/it/titles/70010000006441",
            game.url(country="IT", lang="it")
        )

        self.assertFalse(game.demo)
        self.assertFalse(game.dlc)
        self.assertFalse(game.game_vouchers)
        self.assertFalse(game.nso_required)
        self.assertTrue(game.save_data_cloud)

    def test_noj(self):
        game: SwitchGame = noj.game_info(nsuid="70010000010822")

        self.assertEqual("Celeste", str(game))

        self.assertEqual("70010000010822", game.nsuid)
        self.assertEqual("ACF3", game.unique_id)

        self.assertEqual("Matt Makes Games Inc.", game.developer)
        self.assertEqual("Matt Makes Games", game.publisher)

        self.assertEqual("JP", game.region)
        self.assertEqual("Nintendo Switch", game.platform)

        self.assertEqual(2018, game.release_date.year)
        self.assertEqual(5, game.release_date.month)
        self.assertEqual(10, game.release_date.day)

        self.assertEqual(2, len(game.genres))
        self.assertEqual(9, len(game.languages))
        self.assertEqual(1, game.players)

        self.assertEqual(
            "https://ec.nintendo.com/JP/ja/titles/70010000010822",
            game.url(country="JP", lang="ja")
        )

        self.assertFalse(game.demo)
        self.assertFalse(game.dlc)
        self.assertFalse(game.game_vouchers)
        self.assertFalse(game.nso_required)
        self.assertTrue(game.save_data_cloud)

