"""Add parent directory to path"""
import os,sys,inspect
currentdir_loc = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentdir_loc)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import unittest
import matplotlib
matplotlib.use('Agg')
import cv2

from digit_classifier import load_model
from file_utils import get_img_paths_in_dir
from file_utils import get_paths
from test_settings import ROOT_PATH_2012, ROOT_PATH_2013, ROOT_PATH_2014
from digit_classifier import find_number
from extract_cyclist_faces import load_cache

def get_distance_from_filename(img_name):
    num = img_name.split('/')[-1][:-4]
    return num

def find_classifier_accuracy(root_path):
    """check that the classifier is accurate."""
    paths = get_paths(root_path, "1")
    img_names = get_img_paths_in_dir(paths['digit_testing_frames'])
    cache = load_cache(paths)
    test_nums = [get_distance_from_filename(img_name) for img_name in img_names]
    test_pairs = [(name, target) for (name, target) in zip(img_names, test_nums)]
    accuracy = 0
    for img_name, target in test_pairs:
        number = find_number(img_name, paths, cache['model'], cache['templates'])
        full_num = str(number).replace(".", "")
        if full_num == target:
            accuracy += 1
        else:
            print(img_name)
            print(full_num)
            print('-------')
    return accuracy

class TestDigitClassifier(unittest.TestCase):

    def test_load_model(self):
        """check that load_model returns an instance of 
        a kNN classifier."""
        paths = get_paths(ROOT_PATH_2012, 1)
        model = load_model(paths)
        expected_type = type(cv2.KNearest())
        self.assertEqual(type(model), expected_type)

    def test_2012_classifier_accuracy(self):
        """check classifier accuracy for the 2012 dataset."""
        root_path = ROOT_PATH_2012
        accuracy = find_classifier_accuracy(root_path)
        expected_accuracy = 100
        self.assertEqual(expected_accuracy, accuracy)

    def test_2013_classifier_accuracy(self):
        """check classifier accuracy for the 2013 dataset."""
        root_path = ROOT_PATH_2013
        accuracy = find_classifier_accuracy(root_path)
        expected_accuracy = 100
        self.assertEqual(expected_accuracy, accuracy)

    def test_2014_classifier_accuracy(self):
        """check classifier accuracy for the 2014 dataset."""
        root_path = ROOT_PATH_2014
        accuracy = find_classifier_accuracy(root_path)
        expected_accuracy = 100
        self.assertEqual(expected_accuracy, accuracy)

if __name__ == "__main__":
    unittest.main()
