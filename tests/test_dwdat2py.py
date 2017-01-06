#! /usr/bin/env python

"""Test the local dwdat2py package.
"""

import sys, os
import unittest
import gzip

# Testing the local package code but dependencies need to be available on the
# system.
here = os.path.dirname(__file__)
packdir = os.path.abspath(os.path.join(here, os.pardir))
sys.path.insert(0, packdir)

try:
    from dwdat2py import wrappers as dw
except EnvironmentError as e:
    print e.message
    print 'tests not possible without the lib, please see README.'
    sys.exit(1)

DATAFILE = os.path.join(here, 'Example_Drive01.d7d')

if not os.path.exists(DATAFILE):
    with gzip.open(DATAFILE + '.gz') as fi, open(DATAFILE, 'wb') as fo:
        fo.write(fi.read())


class AttrHolder:
    pass

# a global object to hold module attributes (file info, Channel list)
AH = AttrHolder()

class TestWrappers(unittest.TestCase):
    """Test all the functions in wrappers module."""

    # naming of tests is to ensure execution order
    def test01(self):
        """Test that init() return 0"""

        res = dw.init()
        self.assertEqual(res, 0)

    def test02(self):
        """Test open file and tuple (FileInfo) is returned."""
        AH.dw_fi = dw.open_data_file(DATAFILE)
        self.assertTrue(isinstance(AH.dw_fi, dw.FileInfo))

    def test03(self):
        """Attr's of FileInfo is familiar."""

        self.assertTrue(all([hasattr(AH.dw_fi, 'sample_rate'),
                             hasattr(AH.dw_fi, 'start_store_time'),
                             hasattr(AH.dw_fi, 'duration')]))

    def test04(self):
        """Check that version is higher than zero."""
        version = dw.get_version()
        self.assertGreater(version, 0)

    def test05(self):
        """Number of channels is 20."""
        numchannels = dw.get_channel_list_count()
        self.assertEqual(numchannels, 20)

    def test06(self):
        """Get a channel list and it's a list of Channel tuples"""

        AH.channels = dw.get_channel_list()
        self.assertTrue(all([isinstance(ct, dw.Channel) for ct in AH.channels]))

    def test07(self):
        """Attr's of a Channel in the channel list is familiar."""

        channel = AH.channels[0]
        truelist = [hasattr(channel, 'index'), hasattr(channel, 'name'),
                    hasattr(channel, 'unit'), hasattr(channel, 'description'),
                    hasattr(channel, 'color'), hasattr(channel, 'array_size'),
                    hasattr(channel, 'data_type')]

        self.assertTrue(all(truelist))

    def test08(self):
        """Reduced values count and sample time resolution are all the same."""

        countlist = [dw.get_reduced_values_count(ch.index)
                     for ch in AH.channels]

        self.assertTrue(all([cnt == (192, 0.5) for cnt in countlist]))

    def test09(self):
        """Each item type in the Channel tuples in the list is as expected."""

        truelist = []
        for channel in AH.channels:
            truelist += [type(channel.index) == int,
                         type(channel.name) in (str, unicode),
                         type(channel.unit) in (str, unicode),
                         type(channel.description) in (str, unicode),
                         type(channel.color) in (int, long),
                         type(channel.array_size) == int,
                         type(channel.data_type) == int]

        self.assertTrue(all(truelist))

    def test10(self):
        """get_reduced_values and channel_reduced results in the same data."""

        for channel in AH.channels:
            count, _ = dw.get_reduced_values_count(channel.index)
            records = dw.get_reduced_values(channel.index, 0, count)
            for reduction in range(5):
                self.assertEqual(dw.channel_reduced(channel.index, reduction),
                                     [record[reduction] for record in records])

    def test11(self):
        """The multiplexed argument to channel_reduced (int or str) works."""

        for channel in AH.channels:
            self.assertEqual(dw.channel_reduced(channel.index, 1),
                             dw.channel_reduced(channel.name, 1))


    def test20(self):
        """Test that close file return 0."""
        res = dw.close_data_file()
        self.assertEqual(res, 0)

    def shortDescription(self):
        return None



if __name__ == '__main__':
    unittest.main()
