from unittest import TestCase

import ddt

from nintendeals import exceptions, validate


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
    def test_validate_country(self, string, is_valid):
        @validate.country
        def tmp(*, country: str = ""):
            return country

        if is_valid:
            tmp(country=string)
        else:
            with self.assertRaises(exceptions.InvalidAlpha2Code):
                tmp(country=string)

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
    def test_validate_nsuid(self, string, is_valid):
        @validate.nsuid
        def tmp(*, nsuid: str = ""):
            return nsuid

        if is_valid:
            tmp(nsuid=string)
        else:
            with self.assertRaises(exceptions.InvalidNsuidFormat):
                tmp(nsuid=string)

    @ddt.data(
        ("NA", True),
        ("EU", True),
        ("JP", True),
        ("AS", False),
        ("LA", False),
    )
    @ddt.unpack
    def test_validate_region(self, string, is_valid):
        @validate.region
        def tmp(*, region: str = ""):
            return region

        if is_valid:
            tmp(region=string)
        else:
            with self.assertRaises(exceptions.InvalidRegion):
                tmp(region=string)
