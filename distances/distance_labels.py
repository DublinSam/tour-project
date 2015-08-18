import os
import cv2
import shutil
import string

from snapshot_utils import snapshot
from snapshot_utils import get_video_duration
from snapshot_utils import time_to_seconds, seconds_to_time
from snapshot_cluster import get_dar_dimensions

def formatted_times_in_video(src_video):
    """returns a list of each second of video footage
    formatted in the form 'HH:MM:SS'"""
    duration = get_video_duration(src_video)
    seconds = time_to_seconds(duration)
    times = [seconds_to_time(second) for second in range(seconds)]
    return times

def take_snapshot_every_second(src_video, target_dir, stage_id, DAR):
    """saves a snapshot of src_video every second 
    and saves it to the target_dir."""
    DAR = DAR
    dar_dims = get_dar_dimensions(src_video, DAR=DAR)
    times = formatted_times_in_video(src_video)
    for time in times:
        snapshot(src_video, target_dir, stage_id, 
            time=time, dimensions=dar_dims)

def crop_to_sign(img, x_min_scale=0.05, y_min_scale=0.05, 
                 x_max_scale=0.15, y_max_scale=0.1):
    """crops img to the region specified by the scale 
    parameters."""
    rows, cols = img.shape
    x_min, y_min = cols * x_min_scale, rows * y_min_scale
    x_max, y_max = cols * x_max_scale, rows * y_max_scale
    cropped_img = img[y_min:y_max, x_min:x_max]
    return cropped_img

def is_distance_labeled(img_name, template, sign_region, confidence=0.95):
    """returns true if the template matching achieves the given 
    level of confidence in locating the template.  Otherwise
    returns false."""
    max_val,_ = best_match(img_name, template, sign_region)
    return max_val > confidence

def best_match(img_name, template, sign_region):
    """returns the maximum value and location of the best match 
    found by the template matching method."""
    img = cv2.imread(img_name, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    method = cv2.TM_CCOEFF_NORMED
    cropped_img = crop_to_sign(img, **sign_region)
    result = cv2.matchTemplate(cropped_img, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return (max_val, max_loc)

def find_top_left_sign_corner(img_name, template, sign_region):
    """returns the position of the top left corner of the 'km to go' 
    sign """
    img = cv2.imread(img_name, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    match_val, match_pos = best_match(img_name, template, sign_region)
    flag_position = (match_pos[0] + int(img.shape[1] * sign_region['x_min_scale']),
            match_pos[1] + int(img.shape[0] * sign_region['y_min_scale']))    
    top_left_sign = (flag_position[0] + template.shape[1], flag_position[1])
    return top_left_sign

def find_sign_location(img_name, template, sign_region, width, height):
    """returns the bounding vertices of a rectangular 
    crop frame that encompasses the 'km to go' sign in the given region
    of specified dimensions."""
    top_left_sign_corner = find_top_left_sign_corner(img_name, template, sign_region)
    sign_location = {
        'top_left_x': top_left_sign_corner[0],
        'top_left_y': top_left_sign_corner[1],
        'bottom_right_x': top_left_sign_corner[0] + width,
        'bottom_right_y': top_left_sign_corner[1] + height
    }
    return sign_location

def extract_labeled_snapshots(src_dir, target_dir, template, sign_region):
    all_files = next(os.walk(src_dir))[2]
    imgs = [src_dir + fname for fname in all_files if fname.endswith('.jpg')]
    labeled_imgs = [img for img in imgs if is_distance_labeled(img, 
                                                template, sign_region)]
    for labeled_img in labeled_imgs:
        root, img_name = os.path.split(labeled_img)
        target_name = target_dir + img_name
        shutil.copy(labeled_img, target_name)
