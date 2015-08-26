"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest

from gradients import build_path
from gradients import get_xml_values
from gradients import get_elevations
from gradients import get_precise_distances
from gradients import calculate_gradients
from gradients import find_gradient_at_distance
from gradients import find_gradient

class TestGradients(unittest.TestCase):

    def test_build_path(self):
        """check that build_path correctly concatenates the stage id
        with the required path."""
        stage_id = 5
        path = build_path(stage_id)
        expected_path = "/Users/samuelalbanie/aims_course/project_two/code/tour_data/strava_profiles/raw/Stage5.tcx"
        self.assertEqual(expected_path, path)

    def test_get_xml_values(self):
        """check that get_xml_values is returning a list of 
        values of the correct length."""
        stage_id = 5
        target = "distances"
        expected_num_distances = 2876
        distances = get_xml_values(stage_id, target)
        self.assertEqual(expected_num_distances, len(distances))

    def test_get_elevations(self):
        """check that get_elevations returns a list of floats"""
        stage_id = 3
        elevations = get_elevations(stage_id)
        self.assertTrue(isinstance(elevations[7], float))

    def test_get_precise_distances(self):
        """check that get_precise_distances is working correctly
        by verifying a known value. Note that this is slightly 
        longer than the official stage distance becausee it includes
        the neutral zone at the start."""
        stage_id = 14
        precise_distances = get_precise_distances(stage_id)
        expected_distance = 185082.7 
        full_distance = precise_distances[-1]
        self.assertEqual(expected_distance, full_distance)

    def test_calculate_gradients(self):
        """check that calculate_gradients is working as expected."""
        elevations = [0, 5, 10, 15, 20]
        distances = [0, 10, 20, 30, 40]
        expected_gradients = [0, 50, 50, 50, 50] # first gradient is always 0
        gradients = calculate_gradients(elevations, distances)
        self.assertEqual(expected_gradients, gradients)

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

    def test_tcx_files(self):
        """check the distances for each tcx file to make sure they 
        are correct."""
        stage_data = [{'stage_id': 1, 'length': 206.78},
                      {'stage_id': 2, 'length': 209.00},
                      {'stage_id': 3, 'length': 160.41},
                      {'stage_id': 4, 'length': 173.11},
                      {'stage_id': 5, 'length': 162.03},
                      {'stage_id': 6, 'length': 198.98},
                      {'stage_id': 7, 'length': 243.3},
                      {'stage_id': 8, 'length': 167.84},
                      {'stage_id': 9, 'length': 173.56},
                      {'stage_id': 10, 'length': 177.26},
                      {'stage_id': 11, 'length': 197.67},
                      {'stage_id': 12, 'length': 192.85},
                      {'stage_id': 13, 'length': 206.7},
                      {'stage_id': 14, 'length': 185.08},
                      {'stage_id': 15, 'length': 223.98},
                      {'stage_id': 16, 'length': 244.13},
                      {'stage_id': 17, 'length': 128.79},
                      {'stage_id': 18, 'length': 152.85},
                      {'stage_id': 19, 'length': 211.56},
                      {'stage_id': 20, 'length': 54.1},
                      {'stage_id': 21, 'length': 147.87},
                      ]
        for data in stage_data:
            distances = get_precise_distances(data['stage_id'])
            length = round(max(distances) / 1000, 2)
            expected_length = data['length']
            self.assertEqual(expected_length, length)

    def test_sanity_check_on_gradients_for_climbs(self):
        """check that some steep climbs have large positive 
        gradients."""
        climbs = [{'stage_id': 1, 'km_to_go': 87.8},
                  {'stage_id': 2, 'km_to_go': 59.2},]
        for climb in climbs:
            gradient = find_gradient(climb['stage_id'], climb['km_to_go'])
            self.assertTrue(gradient > 10)
        


if __name__ == "__main__":
    unittest.main()