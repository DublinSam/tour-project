"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest
import numpy as np

import utils

class TestUtils(unittest.TestCase):

    def test_crop_frame(self):
        test_frame = np.zeros((200,300))
        cropped_frame_shape = utils.crop_frame(test_frame).shape
        expected_width = utils.CROP_FRAME['bottom_right_x'] - utils.CROP_FRAME['top_left_x']
        expected_height = utils.CROP_FRAME['bottom_right_y'] - utils.CROP_FRAME['top_left_y']
        expected_shape = (expected_height, expected_width)
        self.assertEqual(expected_shape, cropped_frame_shape)

    def test_get_fig_dimensions(self):
        expected_dims = (3,1)
        fig_dims = utils.get_fig_dimensions()
        self.assertEqual(expected_dims, fig_dims)

    def test_border_rectangle(self):
        test_img = np.zeros((100,200))
        rectangle = utils.border_rectangle(test_img)
        expected_colour = "#777777"
        expected_height = 99
        self.assertEqual(expected_colour, rectangle['edgecolor'])
        self.assertEqual(expected_height, rectangle['height'])


if __name__ == "__main__":
    unittest.main()
