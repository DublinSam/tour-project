import os
import csv
import dlib
import shutil
import pandas as pd

from cycling.utils.file_utils import get_paths
from cycling.utils.time_utils import convert_to_pandas_timestamp

def get_boundaries(paths):
    """returns a list of shot boundary times as pandas
    timestamps."""
    boundaries = []
    with open(paths['shot_boundaries'], 'rb') as csvfile:
        shot_reader = csv.reader(csvfile, delimiter = ',')
        for row in shot_reader:
            boundaries.append(row[0])
    pd_boundaries = [convert_to_pandas_timestamp(boundary) for boundary in boundaries]
    return pd_boundaries

def get_meta_information(paths):
    """returns the meta infomration (times, boxes
    and gradients) associated with each face 
    detection."""
    times, boxes, gradients = [], [], []
    with open(paths['meta'], 'rb') as csvfile:
        box_reader = csv.reader(csvfile, delimiter=',')
        next(box_reader)
        for row in box_reader:
            times.append(row[1])
            boxes.append(row[2])
            gradients.append(row[3])
    meta = {'times': times, 'boxes': boxes, 'gradients': gradients}
    return meta

def format_path(root, stage_id, time, box_idx, gradient, box=None):
    """returns a formatted file path.  If a bounding box is 
    specified, its coordinates are encoded into the path"""
    path = (root + str(stage_id) 
                + '-' + time
                + ':' + str(box_idx) + ':' 
                + str(gradient))
    if box:
        path = (path + ':'
                + str(box['top_left_x']) + ':'
                + str(box['top_left_y']) + ':'
                + str(box['bottom_right_x']) + ':'
                + str(box['bottom_right_y']))
    path = path + '.jpg'
    return path

def is_valid_box(box):
    """returns true if the box is valid (all 
    values are positive)"""
    if min(box.values()) < 0:
        return False
    return True

def get_shot_folder_path(paths, shot_idx, gradient):
    """returns a path to the directory containing all 
    images belonging to the given shot.  If the directory
    doesn't already exist, it is created."""
    shot_folder_path = paths['face_shots'] + str(shot_idx) + '/' + str(gradient) + '/'
    if not os.path.exists(shot_folder_path):
        os.makedirs(shot_folder_path)
    return shot_folder_path

def add_face_to_shot(time, stage_id, shot_idx, box_idx, paths, gradient, box):
    """adds the face detected at the given time to the given shot"""
    src_root = paths['faces']
    src_path = format_path(src_root, stage_id, time, box_idx, gradient)
    dest_root = get_shot_folder_path(paths, shot_idx, gradient)
    dest_path = format_path(dest_root, stage_id, time, box_idx, gradient, box)        
    shutil.copyfile(src_path, dest_path)

def find_shot_id(time, boundaries):
    """returns `shot_idx` which identifies which boundaries 
    the time time lies between."""
    is_before_boundaries = [time < boundary for boundary in boundaries]
    if True in is_before_boundaries:
        shot_idx = is_before_boundaries.index(True)
    else:
        shot_idx = len(boundaries)
    return shot_idx

def group_faces_by_shot(root_path, stage_id):
    """groups faces according to the shot and gradient
    in which they were detected and copies them to a folder 
    representing that shot."""
    paths = get_paths(root_path, stage_id)
    boundaries = get_boundaries(paths)
    meta = get_meta_information(paths)
    pd_times = [convert_to_pandas_timestamp(time) for time in meta['times']]
    for time_idx, pd_time in enumerate(pd_times):
        print(pd_time)
        shot_idx = find_shot_id(pd_time, boundaries)
        gradient = meta['gradients'][time_idx]
        for box_idx, box in enumerate(eval(meta['boxes'][time_idx])):
            if is_valid_box(box):
                add_face_to_shot(meta['times'][time_idx], stage_id, shot_idx, box_idx, paths, gradient, box)
