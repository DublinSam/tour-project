"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest
import numpy as np

from time_utils import time_cluster
from time_utils import offset_time
from time_utils import ensure_two_digits
from time_utils import ensure_three_digits


class TestSnapshotCluster(unittest.TestCase):

    def test_time_cluster(self):
        """check that time_cluster returns a list of correctly
        formatted time strings."""
        time = "00:02:20:000"
        size = 9
        max_offset = 400
        expected_cluster = ["00:02:19:600", "00:02:19:700", 
                            "00:02:19:800", "00:02:19:900",
                            "00:02:20:000", "00:02:20:100",
                            "00:02:20:200", "00:02:20:300",
                            "00:02:20:400"]
        cluster = time_cluster(time, size, max_offset)
        self.assertEqual(expected_cluster, cluster)

    def test_offset_time_with_zero_offset(self):
        """check that offset_time return a correctly formatted
        string for zero offset."""
        initial_time = '00:16:30:000'
        offset = 0 # milliseconds
        expected_time = '00:16:30:000'
        time = offset_time(initial_time, offset)
        self.assertEqual(expected_time, time)

    def test_offset_time_with_positive_offset(self):
        """check that offset_time return a correctly formatted
        string for positive three digit offsets."""
        initial_time = '00:16:30:000'
        offset = 350 # milliseconds
        expected_time = '00:16:30:350'
        time = offset_time(initial_time, offset)
        self.assertEqual(expected_time, time)

    def test_negative_offset_single_digit_seconds(self):
        """check that offset_time return a correctly formatted
        string for positive three digit offsets."""
        initial_time = '00:00:02'
        offset = -150 # milliseconds
        expected_time = '00:00:01:850'
        time = offset_time(initial_time, offset)
        self.assertEqual(expected_time, time)

    def test_offset_time_with_negative_offset(self):
        """check that offset_time return a correctly formatted
        string for negative three digit offsets."""
        initial_time = '00:14:20:000'
        offset = -270 # milliseconds
        expected_time = '00:14:19:730'
        time = offset_time(initial_time, offset)
        self.assertEqual(expected_time, time)

    def test_ensure_two_digits(self):
        """check that ensure_two_digits works correctly with 
        a range of possible inputs"""
        num1 = 0
        expected_num1 = '00'
        num2 = 3
        expected_num2 = '03'
        num3 = 67
        expected_num3 = '67'
        self.assertEqual(expected_num1, ensure_two_digits(num1))
        self.assertEqual(expected_num2, ensure_two_digits(num2))
        self.assertEqual(expected_num3, ensure_two_digits(num3))
        

    def test_ensure_three_digits(self):
        """check that ensure_three_digits works correctly with 
        a range of possible inputs"""
        num1 = 4
        expected_num1 = '004'
        num2 = 36
        expected_num2 = '036'
        num3 = 467
        expected_num3 = '467'
        self.assertEqual(expected_num1, ensure_three_digits(num1))
        self.assertEqual(expected_num2, ensure_three_digits(num2))
        self.assertEqual(expected_num3, ensure_three_digits(num3))

if __name__ == "__main__":
    unittest.main()