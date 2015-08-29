"""This script is a slightly modified version of the 
train_object_detector.py example found in the dlib 
library: http://dlib.net/train_object_detector.py.html"""

import os
import sys
import glob

import dlib
from skimage import io

FACES_PATH = '/Users/samuelalbanie/aims_course/project_two/code/dlib/cycling/big_faces/'

def set_hyperparameters(options):
    """returns an options object with settings for 
    the cyclist face detector.  These were found in a 
    simplistic manner - through trial and experimentation."""
    options.add_left_right_image_flips = True
    options.C = 5
    options.num_threads = 4
    options.be_verbose = True
    options.epsilon = 0.1
    options.detection_window_size = 60 * 60
    return options

def train_detector(path=FACES_PATH):
    """saves a detector object to file as 'detector.svm'.
    This detector has been trained (with HOG features) to 
    recognize the labeled objects in path (described in 
    'training.xml')"""
    options = dlib.simple_object_detector_training_options()
    options = set_hyperparameters(options)
    training_xml_path = os.path.join(path, "training.xml")
    dlib.train_simple_object_detector(training_xml_path, "detector.svm", options)

def print_performance(path=FACES_PATH):
    """prints the accuracy of the detector on both the
    training and test sets."""
    testing_xml_path = os.path.join(path, "testing.xml")
    print("") 
    print("Training accuracy: {}".format(
        dlib.test_simple_object_detector(training_xml_path, "detector.svm")))
    print("Testing accuracy: {}".format(
        dlib.test_simple_object_detector(testing_xml_path, "detector.svm")))

def visualize_detections(path=FACES_PATH):
    """displays the bounding boxes found by the detector, 
    overlaid on top of the example images."""
    detector = dlib.simple_object_detector("detector.svm")
    print("Showing detections on the images in the faces folder...")
    win = dlib.image_window()
    for f in glob.glob(os.path.join(path, "*.jpg")):
        print("Processing file: {}".format(f))
        img = io.imread(f)
        dets = detector(img)
        print("Number of faces detected: {}".format(len(dets)))
        for k, d in enumerate(dets):
            print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                k, d.left(), d.top(), d.right(), d.bottom()))

        win.clear_overlay()
        win.set_image(img)
        win.add_overlay(dets)
        win.wait_until_closed()
        dlib.hit_enter_to_continue()