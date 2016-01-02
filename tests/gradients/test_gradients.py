"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest

from gradients import get_xml_values
from gradients import get_elevations
from gradients import get_precise_distances
from gradients import calculate_gradients
from gradients import find_gradient_at_distance
from gradients import find_gradient
from file_utils import get_paths
from test_settings import ROOT_PATH_2012, ROOT_PATH_2014



class TestGradients(unittest.TestCase):

    def test_get_xml_values(self):
        """check that get_xml_values is returning a list of 
        values of the correct length."""
        stage_id = 5
        target = "distances"
        expected_num_distances = 6034
        paths = get_paths(ROOT_PATH_2012, stage_id)
        distances = get_xml_values(paths, target)
        self.assertEqual(expected_num_distances, len(distances))

    def test_get_elevations(self):
        """check that get_elevations returns a list of floats"""
        stage_id = 3
        paths = get_paths(ROOT_PATH_2012, stage_id)
        elevations = get_elevations(paths)
        self.assertTrue(isinstance(elevations[7], float))

    def test_get_precise_distances(self):
        """check that get_precise_distances is working correctly
        by verifying a known value. Note that this is slightly 
        longer than the official stage distance becausee it includes
        the neutral zone at the start."""
        stage_id = 14
        paths = get_paths(ROOT_PATH_2012, stage_id)
        precise_distances = get_precise_distances(paths)
        expected_distance = 194769.4 
        full_distance = precise_distances[-1]
        self.assertEqual(expected_distance, full_distance)

    def test_find_gradient_at_distance(self):
        """check that find_gradient_at_distance works as 
        expected with known values."""
        gradients = [15, 13, 14, 17, 19]
        distances = [0, 10, 20, 30, 40]
        target_distance1 = 26
        expected_gradient1 = 17
        gradient1 = find_gradient_at_distance(target_distance1, distances, gradients)
        # When the target distance is equidistant, the first gradient 
        # will be chosen
        target_distance2 = 25
        expected_gradient2 = 14
        gradient2 = find_gradient_at_distance(target_distance2, distances, gradients)
        self.assertEqual(expected_gradient1, gradient1)
        self.assertEqual(expected_gradient2, gradient2)

if __name__ == "__main__":
    unittest.main()
