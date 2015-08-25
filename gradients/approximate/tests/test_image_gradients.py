"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest

from image_gradients import Stage

class TestGradients(unittest.TestCase):

    def test_find_stage_dims(self):
        """check that find_stage_dims correctly retrieves the 
        dimensions for the stage represented by the class."""
        stage = Stage(9) # __init__ calls find_stage_dims()
        expected_length = 28000
        expected_max_altitude = 153
        self.assertEqual(stage.stage_dims['length'], expected_length)
        self.assertEqual(stage.stage_dims['max altitude'], expected_max_altitude)

    def test_trace_is_a_single_pixel_thick(self):
        """build_trace should construct an array containing a trace a single
        pixel thick representing the stage profile."""
        stage = Stage(11)
        expected_num_of_values = 1
        for col in stage.trace.T:
            self.assertTrue((col == 1).sum() <= expected_num_of_values)

    def test_get_non_zero_cols(self):
        """check that columns containing part of the trace are 
        detected correctly."""
        stage = Stage(12)
        expected_indices = list(range(2,595))
        indices = stage.get_non_zero_cols(stage.trace)
        self.assertEqual(indices, expected_indices)

    def test_trace_dimensions(self):
        """check trace_dimensions are retrieved correcly."""
        stage = Stage(14) # find_trace_dimensions() is called by __init__
        expected_trace_dims = {
                        'min_y': 137, 
                        'min_x': 0, 
                        'max_y': 229, 
                        'max_x': 593}
        self.assertEqual(stage.trace_dims, expected_trace_dims)

    def test_relative_altitude(self):
        """check that relative altitude works correctly."""
        stage = Stage(1)
        pixel_x = 40
        expected_rel_altitude = 0.25
        self.assertEqual(stage.relative_altitude(pixel_x), expected_rel_altitude)

    def test_altitude(self):
        """check altitude function with a known value for a specific stage."""
        stage = Stage(12)
        pixel_x = 594
        expected_altitude = 1780
        self.assertEqual(stage.altitude(pixel_x), expected_altitude)

    def test_km_to_pixel(self):
        """check km_to_pixel works correctly with a known value."""
        stage = Stage(12)
        km = 3
        expected_pixel = 11
        self.assertEqual(stage.km_to_pixel(km), expected_pixel)

    def test_slope_to_degrees(self):
        """check that gradients are correctly converted to degrees"""
        stage = Stage(1)
        grad0 = 0
        degrees0 = 0
        grad1 = 1
        degrees1 = 45
        self.assertEqual(stage.slope_to_degrees(grad0), degrees0)
        self.assertEqual(stage.slope_to_degrees(grad1), degrees1)

    def test_gradient(self):
        """check the gradient function calculates the gradient accurately."""
        stage = Stage(12)
        daspet_ascent = 57.5
        climb_dist = 9.7
        expected_degrees = 6.205696557596017
        degrees = stage.gradient(daspet_ascent, climb_dist)
        self.assertAlmostEqual(degrees, expected_degrees)

    def test_get_climbs(self):
        stage = Stage(12)
        stage.get_climbs()
        expected_length = 4.3
        self.assertEqual(stage.climbs[0]['length'], expected_length)

    def test_set_calibration_factor(self):
        """check calibration factor operates correctly."""
        stage = Stage(12)
        expected_factor = 0.52175771994330411
        self.assertAlmostEqual(stage.calib_factor, expected_factor)

if __name__ == "__main__":
    unittest.main()