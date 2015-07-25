"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest
import cv2

from digit_classifier import load_model

class TestDigitClassifier(unittest.TestCase):

    def test_load_model(self):
        """check that load_model returns an instance of 
        a kNN classifier."""
        model = load_model()
        expected_type = type(cv2.KNearest())
        self.assertEqual(type(model), expected_type)

if __name__ == "__main__":
    unittest.main()