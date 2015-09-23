"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest
import numpy as np

from image_utils import crop_frame
from image_utils import border_rectangle
from image_utils import get_fig_dimensions

class TestUtils(unittest.TestCase):

    def test_crop_frame(self):
        test_frame = np.zeros((200,300))
        region = {
            'top_left_x': 0,
            'top_left_y': 0, 
            'bottom_right_x': 100, 
            'bottom_right_y': 100,
        }
        cropped_frame_shape = crop_frame(test_frame, region).shape
        expected_width = region['bottom_right_x'] - region['top_left_x']
        expected_height = region['bottom_right_y'] - region['top_left_y']
        expected_shape = (expected_height, expected_width)
        self.assertEqual(expected_shape, cropped_frame_shape)

    def test_get_fig_dimensions(self):
        expected_dims = (1.5, 1)
        width, height = 15, 10
        fig_dims = get_fig_dimensions(width, height)
        self.assertEqual(expected_dims, fig_dims)

    def test_border_rectangle(self):
        test_img = np.zeros((100,200))
        rectangle = border_rectangle(test_img)
        expected_colour = "#777777"
        expected_height = 99
        self.assertEqual(expected_colour, rectangle['edgecolor'])
        self.assertEqual(expected_height, rectangle['height'])


if __name__ == "__main__":
    unittest.main()
