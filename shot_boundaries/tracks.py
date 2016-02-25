from __future__ import division

import os
import shutil
from IPython.core.debugger import Tracer
from cycling.utils.file_utils import get_paths, get_img_paths_in_dir
from cycling.utils.time_utils import convert_to_pandas_timestamp

def parse_box(img_path):
    """parses the box description from the img path
    and returns a dictionary describing a box."""
    box = {}
    parts = img_path.split(':')
    box['top_left_x'] = int(parts[-4])
    box['top_left_y'] = int(parts[-3])
    box['bottom_right_x'] = int(parts[-2])
    box['bottom_right_y'] = int(parts[-1].split('.')[0])
    return box

def box_area(box):
    """returns the area of a box described by its
    corners."""
    width = box['bottom_right_x'] - box['top_left_x']
    height = box['bottom_right_y'] - box['top_left_y']
    return width * height

def order_boxes_by_size(box1, box2):
    """returns the boxes, ordered in increasing 
    size order. If the size is the same, the 
    ordering is arbitrary."""
    if box_area(box1) < box_area(box2):
        return (box1, box2)
    return (box2, box1)

def intersection_area(box1, box2):
    """returns the area of the intersection between 
    the two boxes."""
    top_boundary = max(box1['top_left_y'], box2['top_left_y'])    
    bottom_boundary = min(box1['bottom_right_y'], box2['bottom_right_y'])
    left_boundary = max(box1['top_left_x'], box2['top_left_x'])
    right_boundary = min(box1['bottom_right_x'], box2['bottom_right_x'])
    width = right_boundary - left_boundary
    height = bottom_boundary - top_boundary
    return width * height

def get_shots_subdirs(paths):
    """returns all subdirectories containing gradient 
    labeled shots"""
    shot_dir = paths['face_shots']
    shot_subdirs = [shot_dir + name + '/' for name in os.listdir(shot_dir)
            if os.path.isdir(os.path.join(shot_dir, name))]
    all_gradient_shot_subdirs = []
    for shot_subdir in shot_subdirs:
        gradient_shot_subdirs = [shot_subdir + name + '/' for name in os.listdir(shot_subdir)
            if os.path.isdir(os.path.join(shot_subdir, name))]
        all_gradient_shot_subdirs.append(gradient_shot_subdirs)
    return all_gradient_shot_subdirs

def parse_stage_id(img_path):
    """parses the stage id from the img_path"""
    name = img_path.split('/')[-1]
    stage_id = str(name.split('-')[0])
    return stage_id

def parse_gradient(img_path):
    """returns the gradient descrbied in the img_path."""
    name = img_path.split('/')[-1]
    gradient = str(name.split(':')[-5])
    return gradient

def parse_time_string(img_path):
    """parses the time string from the img_path."""
    name = img_path.split('/')[-1]
    short_name = name.split('-')[1]
    time_string = ":".join(short_name.split(":")[0:4])
    return time_string

def parse_box_idx(img_path):
    """returns the id of the box within the frame"""
    meta = img_path.split('/')[-1]
    box_idx = int(meta.split(':')[4])
    return box_idx

def parse_time(img_path):
    """returns a pandas timestamp representing 
    the time at which the face was extracted."""
    meta = img_path.split('/')[-1]
    stamp = meta.split('-')[1]
    time = '-'.join(stamp.split(':')[0:4])
    return convert_to_pandas_timestamp(time)

def is_overlapping(box1, box2, threshold=0.8):
    """returns true if there is sufficient overlap
    between the two boxes. Overlap is measured as 
    the percentage of the smaller box that overlaps the
    larger box."""
    smaller, larger = order_boxes_by_size(box1, box2)
    intersection = intersection_area(box1, box2)
    overlap = intersection / box_area(smaller)
    print('smaller area: ' + str(box_area(smaller)))
    print('overlap: ' + str(overlap))
    return overlap > threshold

def parse_img_name(img_path):
    """returns the image name conainted in the
    img_path."""
    return img_path.split('/')[-1]

class FaceTrack:
    
    def __init__(self, img_path, max_history=2, threshold=0.8):
        self.faces = [img_path,]
        self.threshold = threshold
        self.max_history = max_history
        self.start_time = parse_time(img_path)
        self.latest_time = parse_time(img_path)
        self.recent_boxes = [parse_box(img_path), ]
        
    def check_match(self, img_path):
        """tries to find a match with a box already 
        in the track."""
        new_box = parse_box(img_path)
        new_time = parse_time(img_path)
        time_diff = (new_time - self.latest_time).total_seconds()
        candidate_boxes = self.recent_boxes[:self.max_history]
        for box in candidate_boxes:
            if is_overlapping(box, new_box, self.threshold) and time_diff < 0.1:
                return True
        return False
        
    def merge(self, img_path):
        """merges the given image into the FaceTrack
        """
        self.faces.append(img_path)
        self.recent_boxes.insert(0, parse_box(img_path))
        self.latest_time = parse_time(img_path)
    
    def display(self):
        """prints the details of the face track."""
        print("Track Length: ", len(self.faces))
        print("Start time: ", self.start_time)
        print("Finish time: ", self.latest_time)
        for idx, img_path in enumerate(self.faces):
            print("Face #" + str(idx + 1) + ": " + parse_img_name(img_path))
            
    def transfer(self, paths, track_idx):
        root = paths['face_tracks']
        for img_path in self.faces:
            track_dir = root + str(track_idx) + '/'
            if not os.path.exists(track_dir):
                os.makedirs(track_dir)
            gradient = parse_gradient(img_path)
            stage_id = parse_stage_id(img_path)
            time = parse_time_string(img_path)
            dest = track_dir  + stage_id + '-' + time + ':' + gradient + '.jpg'
            shutil.copyfile(img_path, dest)

def find_tracks(img_paths):
    """searches the given list of img_paths 
    and sorts them into face tracks."""
    faceTracks = []
    for img_path in sorted(img_paths):
        for faceTrack in faceTracks:
            if faceTrack.check_match(img_path):
                faceTrack.merge(img_path)
                print('Extended track!')
                break
        else:
            newTrack = FaceTrack(img_path, max_history=2, threshold=0.5)
            faceTracks.append(newTrack)
            print('new track!')
    return faceTracks

def extract_face_tracks(root_path, stage_id):
    """searches through the formatted faces and clusters
    them into tracks by time and location."""
    paths = get_paths(root_path, stage_id)
    counter = 1
    subdirs = get_shots_subdirs(paths)
    for subdir in subdirs:
        for shotdir in subdir:
            img_paths = sorted(get_img_paths_in_dir(shotdir))
            tracks = find_tracks(img_paths)
            for track in tracks:
                track.transfer(paths, counter)
                counter = counter + 1
