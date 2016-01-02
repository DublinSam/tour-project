"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest
import cv2

from test_settings import ROOT_PATH_2012
from camera import CameraFocus

class TestCamera(unittest.TestCase):

    def test_camera_initializes_correctly(self):
        """check that load_model returns an instance of 
        a kNN classifier."""
        stage_id = 8
        camera_focus = CameraFocus(ROOT_PATH_2012, stage_id)
        expected_num_precis_frames = 1029
        num_precis_frames = len(camera_focus.frames)
        self.assertEqual(expected_num_precis_frames, num_precis_frames)

if __name__ == "__main__":
    unittest.main()
