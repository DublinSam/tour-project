import os
import cv2
import shutil
import pickle
import matplotlib.pyplot as plt

from tqdm import *
from file_utils import get_paths
from digit_classifier import load_model
from digit_classifier import find_number
from template_matching import get_templates 
from template_matching import contains_tete_template
from template_matching import contains_chequered_flag
from template_matching import contains_group_positions
from template_matching import contains_poursuivants_template
from template_matching import is_distance_measured_in_km

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
        if not self.is_distance_labeled(img):
            self.current_camera_state = Camera.Rest
        else:
            self.update_breakaway_state(img, img_name)

    def update_breakaway_state(self, img, img_name):
        # reset the camera focus to the pursuers if the footage
        # jumps
        if self.did_footage_skip(img_name):
            self.current_camera_state = Camera.Poursuivants

        # First check for an annotation describing the spacing
        # between all groups in the race. This often accompanies
        # a switch of camera focus, but doesn't indicate which so
        # we conservatively reset to Poursuivants
        elif contains_group_positions(img, self.templates):
            self.current_camera_state = Camera.Poursuivants
        
        elif contains_tete_template(img, self.templates):
            self.current_camera_state = Camera.Tete

        # If not, we check for an annotation that the camera is 
        # focused on the pursuers.

        elif contains_poursuivants_template(img, self.templates):
            self.current_camera_state = Camera.Poursuivants

        # Otherwise, we maintain the current state unless the 
        # racing footage has just begun, in which case we assume 
        # that the camera is following the head of the stage.
        else: 
            if self.current_camera_state == Camera.Rest:
                self.current_camera_state = Camera.Tete
            else:
                pass # maintain the current state

    def did_footage_skip(self, img_name):
        """Sometimes the cycling footage jumps in time, making the 
        current camera focus state invalid.  We can check this by 
        noticing a jump in the "km to go" sign."""
        did_skip = False
        if self.current_distance:
            previous_distance = self.current_distance
            self.current_distance = find_number(img_name, self.paths, self.digit_model, self.templates)
            if previous_distance - self.current_distance > 0.15:
                did_skip = True
        else:
            self.current_distance = find_number(img_name, self.paths, self.digit_model, self.templates)
        return did_skip

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

    def save_camera_states(self):
        """pickle the camera states so that they can be 
        retrieved later in processing."""
        with open(self.paths['log'], 'wb') as f:
            pickle.dump(self.camera_states_log, f)
