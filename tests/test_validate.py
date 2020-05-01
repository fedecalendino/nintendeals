from unittest import TestCase

import ddt

from nintendeals import validate, exceptions


@ddt.ddt
class TestValidate(TestCase):

    @ddt.data(
        ("AR", True),
        ("CZ", True),
        ("XX", False),
        ("ITA", False),
        ("C", False),
    )
    @ddt.unpack
    def test_alpha_2(self, string, is_valid):
        if is_valid:
            validate.alpha_2(string)
            return

        with self.assertRaises(exceptions.InvalidAlpha2Code):
            validate.alpha_2(string)

    @ddt.data(
        ("70010000000025", True),
        ("10010123456789", True),
        ("71210000000023", False),
        ("700100000000", False),
        ("0000000023", False),
        (70010000000023, False),
        (70010000000026, False),
    )
    @ddt.unpack
    def test_nsuid_format(self, string, is_valid):
        if is_valid:
            validate.nsuid_format(string)
            return

        with self.assertRaises(exceptions.InvalidNsuidFormat):
            validate.nsuid_format(string)

    @ddt.data(
        ("NA", True),
        ("EU", True),
        ("JP", True),
        ("AS", False),
        ("LA", False),
    )
    @ddt.unpack
    def test_nintendo_region(self, string, is_valid):
        if is_valid:
            validate.nintendo_region(string)
            return

        with self.assertRaises(exceptions.InvalidRegion):
            validate.nintendo_region(string)
