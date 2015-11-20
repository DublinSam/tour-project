import os
import cv2
import csv
import shutil
import pickle
import matplotlib.pyplot as plt

from tqdm import *
from file_utils import get_paths
from time_utils import format_time
from time_utils import get_time_from_path
from digit_classifier import load_model
from digit_classifier import find_number
from template_matching import get_templates 
from template_matching import contains_tete_template
from template_matching import contains_chequered_flag
from template_matching import contains_group_positions
from template_matching import contains_poursuivants_template
from template_matching import is_distance_measured_in_km
from template_matching import is_poursuivants_marker_frame 
from template_matching import is_tete_marker_frame 

from file_utils import get_img_paths_in_dir


class Camera:
    """This class enumerates the possible states of focus for 
    the camera producing race footage.
        * Rest: Currently, the camera is not following the race
        * Tete: Currently, the camera is following the stage leader
        * Poursuivants: Currently, the camera is following the 
          pursuers"""
    Rest = 0
    Tete = 1 
    Poursuivants = 2

class CameraFocus:

    def __init__(self, root_path, stage_id):
        """takes as input a directory containing frames i.e. 
        snapshots taken at a one second interval."""
        self.paths = get_paths(root_path, stage_id)
        self.frames = sorted(get_img_paths_in_dir(self.paths['precis']))
        self.stage_id = stage_id
        self.current_camera_state = Camera.Rest
        self.camera_states_log = []
        self.digit_model = load_model(self.paths)
        self.current_distance = None
        self.templates = get_templates(self.paths)
        self.annotations = self.load_manual_annotations(self.paths)

    def get_camera_states(self):
        # First check if camera states log already exists
        log_file = self.paths['log']
        if os.path.isfile(log_file):
            with open(log_file, 'rb') as f:
                self.camera_states_log = pickle.load(f)
        else:
            # otherwise, create it from scratch
            for img_name in tqdm(self.frames):
                img = cv2.imread(img_name, cv2.CV_LOAD_IMAGE_GRAYSCALE) 
                self.update_camera_state(img, img_name)
                self.camera_states_log.append(self.current_camera_state)
        return self.camera_states_log


    def update_camera_state(self, img, img_name):
        # First check for manual annotations        
        time = get_time_from_path(img_name)
        if time in self.annotations.keys():
            self.update_annotated_state(time)
        elif not self.is_distance_labeled(img):
            self.current_camera_state = Camera.Rest
        else:
            pass

    def update_annotated_state(self, time):
        if self.annotations[time] == 'T':
            self.current_camera_state = Camera.Tete
        else:
            self.current_camera_state = Camera.Poursuivants

    def is_distance_labeled(self, img):
        """returns true if the image contains BOTH a chequred flag 
        and the distance is measured in km."""
        has_flag = contains_chequered_flag(img, self.templates['flag'])
        if has_flag:
            in_km = is_distance_measured_in_km(img, self.templates)
        return has_flag and in_km

    def visualize(self, **kwargs):
        """plot a grap illustrating the camera focus 
        transitions.""" 
        idx = range(len(self.camera_states_log))
        plt.plot(idx, self.camera_states_log, **kwargs)

    def load_manual_annotations(self, paths):
        """load manual annotations from csv import file"""
        annotations = {}
        with open(paths['annotations'], 'rU') as f:
            reader = csv.reader(f)
            next(reader, None) # skip headers
            for row in reader:
                hours = int(row[0])
                mins = int(row[1])
                secs = int(row[2])
                state = row[3]
                time = format_time(hours, mins, secs)
                annotations[time] = state
        return annotations
                

    def save_camera_states(self):
        """pickle the camera states so that they can be 
        retrieved later in processing."""
        with open(self.paths['log'], 'wb') as f:
            pickle.dump(self.camera_states_log, f)
