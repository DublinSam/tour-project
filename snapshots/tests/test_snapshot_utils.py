"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest
import numpy as np

from snapshot_utils import clean_msg
from snapshot_utils import get_num_frames

class TestUtils(unittest.TestCase):

    def test_get_num_frames(self):
        """check that get_num_frames correctly 
        calculates the number of frames in a given
        time period."""
        duration = "01:13:12"
        fps = 29
        expected_num_frames = 127368
        num_frames = get_num_frames(duration, fps)
        self.assertEqual(expected_num_frames, num_frames)

    def test_clean_msg(self):
        """check that clean_msg removes the 
        expected characters."""
        sample = "here is \n a msg with \n in it"
        expected = "hereisamsgwithinit"
        cleaned = clean_msg(sample)
        self.assertEqual(expected, cleaned)

if __name__ == "__main__":
    unittest.main()