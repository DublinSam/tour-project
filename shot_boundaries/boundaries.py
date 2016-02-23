import csv
import cv2
import numpy as np
from datetime import datetime
from cycling.utils.file_utils import get_img_paths_in_dir, get_paths
from cycling.utils.time_utils import get_time_from_path

# Define the minimum number of seconds between 
MIN_SHOT_LENGTH = 4 

def save_boundaries(root_path, stage_id):
    """saves the shot boundaries data associated with a specific
    stage as a csv."""
    paths = get_paths(root_path, stage_id)
    img_paths = sorted(get_img_paths_in_dir(paths['dense_tete']))
    shot_boundaries = find_boundaries(img_paths)

    with open(paths['shot_boundaries'], 'wb') as f:
        writer = csv.writer(f)
        for boundary in shot_boundaries:        
            writer.writerow([boundary])

def get_hist(img_path):
    """returns a normalized, flattened colour histogram of the 
    image specified."""
    img = cv2.imread(img_path)
    color_hist = cv2.calcHist(images=[img], channels=[0,1,2], mask=None,
            histSize=[16, 16, 16], ranges=[0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(color_hist).flatten()
    return hist

def find_boundaries(img_paths):
    """returns a list of times at which shot boundaries occur. Times are 
    given in the format HH:MM:SS:MMM where
    HH: Hours, MM: Minutes, SS: Seconds, MMM: milliseconds."""
    shot_boundaries = [get_time_from_path(img_paths[0])]
    for prev, now in zip(img_paths, img_paths[1:]):
        hist_prev = get_hist(prev)
        hist_now = get_hist(now)
        dist = cv2.compareHist(hist_prev, hist_now, cv2.cv.CV_COMP_CHISQR)
        # time = "".join(now.split('-')[-1][:-4])
        time = get_time_from_path(now)

        if dist > 5:
            if time_diff(shot_boundaries[-1], time) > MIN_SHOT_LENGTH:
                shot_boundaries.append(time)
    return shot_boundaries

def time_diff(earlier, later):
    """returns the difference betweeen the given times in 
    seconds."""
    FMT = '%H:%M:%S:%f'
    time1 = datetime.strptime(earlier + '000',FMT) 
    time2 = datetime.strptime(later + '000',FMT)
    delta = (time2 - time1).total_seconds()
    return delta
