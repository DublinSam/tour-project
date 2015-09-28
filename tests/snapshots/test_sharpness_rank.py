"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest
import numpy as np

from sharpness_rank import focus_on_center
from sharpness_rank import high_pass_filter

class TestSnapshotCluster(unittest.TestCase):

    def test_focus_on_center_returns_correct_dims(self):
        """check that focus_on_center returns a cropped
        image of the appropriate dimensions."""
        sample_img = np.zeros((400, 200))
        scale = 0.5
        expected_dims = (200,100)
        focused_img = focus_on_center(sample_img, scale)
        dims = focused_img.shape
        self.assertEqual(expected_dims, dims)

    def test_high_pass_filter(self):
        """check that high_pass_filter sets low 
        frequencies to near zero."""
        spectrum2d = np.ones((400,400))
        filter_size = 100
        filtered = high_pass_filter(spectrum2d, filter_size)
        lower_freqs = filtered[100:300, 100:300]
        for elem in np.nditer(lower_freqs):
            self.assertTrue(elem < 0.00001)

if __name__ == "__main__":
    unittest.main()

