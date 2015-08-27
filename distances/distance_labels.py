import os
import cv2
import shutil
import string

from utils import crop_frame
from snapshot_utils import snapshot
from snapshot_utils import get_video_duration
from snapshot_utils import time_to_seconds, seconds_to_time
from snapshot_cluster import get_dar_dimensions

PATH = '/Users/samuelalbanie/aims_course/project_two/code/DVD/'
TEMPLATE_PATH = PATH + 'templates/'
FLAG_PATH = TEMPLATE_PATH + 'flag.jpg'
KM_PATH = TEMPLATE_PATH + 'km_sign.jpg'

# These hardcoded values were found by trial and error 
# on a bunch of images

# Define the width and height of the 'km to go' sign 
SIGN_WIDTH = 200
SIGN_HEIGHT = 20

def crop_to_scaled_region(img, x_min_scale=0.05, y_min_scale=0.05, 
                 x_max_scale=0.15, y_max_scale=0.1):
    """crops img to the region specified by the scale 
    parameters."""
    rows, cols = img.shape
    x_min, y_min = cols * x_min_scale, rows * y_min_scale
    x_max, y_max = cols * x_max_scale, rows * y_max_scale
    cropped_img = img[y_min:y_max, x_min:x_max]
    return cropped_img

def formatted_times_in_video(src_video):
    """returns a list of each second of video footage
    formatted in the form 'HH:MM:SS'"""
    duration = get_video_duration(src_video)
    seconds = time_to_seconds(duration)
    times = [seconds_to_time(second) for second in range(seconds)]
    return times

def best_match(img, template):
    """returns the maximum value and location of the best match 
    found by the template matching method."""
    method = cv2.TM_CCOEFF_NORMED
    result = cv2.matchTemplate(img, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return (max_val, max_loc)

def find_top_left_corner(img, template):
    """returns the position of the top left corner of the 
    region bounded on the left by the location of the template."""
    match_val, match_pos = best_match(img, template)
    top_left_sign = (match_pos[0] + template.shape[1], match_pos[1])
    return top_left_sign

def find_sign_location(img, template, width=SIGN_WIDTH, height=SIGN_HEIGHT):
    """returns the bounding vertices of a rectangular 
    crop frame that encompasses the 'km to go' sign in the given region
    of specified dimeansions."""
    top_left_corner = find_top_left_corner(img, template)
    sign_location = {
        'top_left_x': top_left_corner[0],
        'top_left_y': top_left_corner[1],
        'bottom_right_x': top_left_corner[0] + width,
        'bottom_right_y': top_left_corner[1] + height
    }
    return sign_location

def contains_template(img, template, confidence):
    """returns true if the template matching achieves the 
    given level of confidence in locating the template.
    Otherwise returns false."""
    max_val,_ = best_match(img, template)
    return max_val > confidence

def crop_to_sign(img, flag_template):
    """returns a cropped frame containing just the 
    'km to go sign'"""
    sign_location = find_sign_location(img, flag_template)
    cropped_frame = crop_frame(img, sign_location)
    return cropped_frame

def contains_chequered_flag(img, template, confidence):
    """returns true if the image contains a chequered 
    flag in SIGN_REGION"""
    sign_frame = crop_to_sign(img, template)
    has_flag = contains_template(sign_frame, template, confidence)
    return has_flag

def is_distance_measured_in_km(img, templates):
    """returns true if the distance on the 'to go' sign is 
    measured in km (i.e. it contains the 'km' template)."""
    sign_location = find_sign_location(img, templates['flag'])
    cropped_img = crop_frame(img, sign_location)
    in_km = contains_template(cropped_img, templates['km'], confidence)
    return in_km

def is_distance_labeled(img_name, templates, confidence=0.95):
    """returns true if the image contains BOTH a chequred flag 
    and the distance is measured in km."""
    img = cv2.imread(img_name, cv2.CV_LOAD_IMAGE_GRAYSCALE)              
    has_flag = contains_chequered_flag(img, templates['flag'], confidence)
    in_km = is_distance_measured_in_km(img, templates)
    return has_flag and in_km

def get_templates(flag_path=FLAG_PATH, km_path=KM_PATH):
    """returns the templates at the given paths. This is 
    done for caching purposes."""
    flag_template = cv2.imread(flag_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    km_template = cv2.imread(km_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    templates = {'flag': flag_template, 'km': km_template}
    return templates

def take_snapshot_every_second(src_video, target_dir, stage_id, DAR):
    """saves a snapshot of src_video every second 
    and saves it to the target_dir."""
    DAR = DAR
    dar_dims = get_dar_dimensions(src_video, DAR=DAR)
    times = formatted_times_in_video(src_video)
    for time in times:
        snapshot(src_video, target_dir, stage_id, 
            time=time, dimensions=dar_dims)

def extract_labeled_snapshots(src_dir, target_dir):
    all_files = next(os.walk(src_dir))[2]
    imgs = [src_dir + fname for fname in all_files if fname.endswith('.jpg')]
    templates = get_templates()
    labeled_imgs = [img for img in imgs if is_distance_labeled(img, templates)]
    for labeled_img in labeled_imgs:
        root, img_name = os.path.split(labeled_img)
        target_name = target_dir + img_name
        shutil.copy(labeled_img, target_name)

def digit_region(img, region_width=52):
    """returns the region of the image containg the digits
    representing the distance to go. The img must contain 
    the 'km to go' sign."""
    templates = get_templates()
    sign_frame = crop_to_sign(img, templates['flag'])
    score, loc = best_match(sign_frame, templates['km'])
    region_width = 52
    digit_location = {'top_left_x': loc[0] - region_width,
                      'top_left_y': 0,
                      'bottom_right_x': loc[0],
                      'bottom_right_y': loc[1] + templates['km'].shape[0]}
    digits_frame = crop_frame(sign_frame, digit_location)
    return digits_frame
