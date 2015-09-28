"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest
import numpy as np

from test_settings import ROOT_PATH
from file_utils import get_jpgs_in_dir
from file_utils import get_img_paths_in_dir

class TestFileUtils(unittest.TestCase):

    def test_get_jpgs_in_dir(self):
        """Check that get_jpgs_in_dir functions correctly on
        a directoyr of training images.  Since we don't care 
        about ordering, we compare sets of files rather than lists."""
        image_dir = ROOT_PATH + 'ocr/training_images/'
        expected_frames = [
            'contains_136.jpg',
            'contains_137.jpg',
            'contains_138.jpg',
            'contains_139.jpg',
            'contains_1234.jpg',
            'contains_1235.jpg',
            'contains_1320.jpg']
        root, frames = get_jpgs_in_dir(image_dir)
        self.assertEqual(set(expected_frames), set(frames))

    def test_get_img_paths_in_dir(self):
        """Check that get_jpgs_in_dir functions correctly on
        a directoyr of training images.  Since we don't care 
        about ordering, we compare sets of files rather than lists."""
        image_dir = ROOT_PATH + 'ocr/training_images/'
        expected_paths = [
            ROOT_PATH + 'ocr/training_images/contains_136.jpg',
            ROOT_PATH + 'ocr/training_images/contains_137.jpg',
            ROOT_PATH + 'ocr/training_images/contains_138.jpg',
            ROOT_PATH + 'ocr/training_images/contains_139.jpg',
            ROOT_PATH + 'ocr/training_images/contains_1234.jpg',
            ROOT_PATH + 'ocr/training_images/contains_1235.jpg',
            ROOT_PATH + 'ocr/training_images/contains_1320.jpg']
        img_paths = get_img_paths_in_dir(image_dir)
        self.assertEqual(set(expected_paths), set(img_paths))


if __name__ == "__main__":
    unittest.main()
