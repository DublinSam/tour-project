import os
import dlib
import matplotlib
import csv
from tqdm import *
from skimage import io
from file_utils import get_paths
from file_utils import get_jpgs_in_dir
from image_utils import crop_frame
from gradients import find_gradient
from template_matching import get_templates
from digit_classifier import load_model
from digit_classifier import find_number

# The primary cache used to store bounding boxes, times and gradients
META_DATA = [] 

def load_cache(paths):
    """load items that will be used repeatedly into memory
    to avoid unnecessary IO."""
    cache = {}
    cache['paths'] = paths
    cache['model'] = load_model(paths)
    cache['detector'] = dlib.fhog_object_detector(paths['dlib_detector']) 
    cache['templates'] = get_templates(paths)
    return cache

def get_target_dir(target_dir):
    """ensures that target_dir exists"""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir

def save_meta_data(paths):
    """saves the meta data associated with each image to 
    file as a csv."""
    with open(paths['meta'], 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(['stage', 'time', 'bounding boxes', 'gradient'])
        writer.writerows(META_DATA)
        
def get_bounding_boxes(dets):
    """returns a list of dictionaries containing
    the bounding vertices of each detection."""
    bounding_boxes = []
    for box in dets:
        bounding_box = {'top_left_x': box.left(),
                        'top_left_y': box.top(),
                        'bottom_right_x': box.right(),
                        'bottom_right_y': box.bottom()}
        bounding_boxes.append(bounding_box)
    return bounding_boxes

def save_labeled_face(img_name, img, i, box, gradient, cache):
    """Saves face `i` in `img` with a new filename that 
    includes the gradient at which the snapshot was taken."""
    face_img = crop_frame(img, box)
    face_dims = face_img.shape
    head, tail = os.path.split(img_name)
    face_name = tail[:-4] + ':' + str(i) + ':' + str(gradient) + '.jpg'
    if face_dims[0] > 10 and face_dims[1] > 10:
        dest_dir = get_target_dir(cache['paths']['faces'])
        matplotlib.image.imsave(dest_dir + face_name, face_img)

def store_bounding_boxes(img_name, confident_boxes, gradient, cache):
    """Saves the bounding boxes, times and gradients for each 
    facae found"""
    record = [cache['paths']['stage'], img_name[-16:-4], confident_boxes, gradient]
    META_DATA.append(record)

def extract_confident_detections(img, img_name, dets, scores, cache):
    """For the given image, the gradient is calculated and
    passed to 'save_labeled_face()' for detections 
    that meet the required score threshold."""
    distance_to_go = find_number(img_name, cache['paths'], cache['model'], cache['templates'])
    gradient = find_gradient(cache['paths'], distance_to_go)
    bounding_boxes = get_bounding_boxes(dets)
#    for i, box in enumerate(bounding_boxes):
#            if scores[i] > 0.5:
#                save_labeled_face(img_name, img, i, box, gradient, cache)
    confident_boxes = [pair[1] for pair in enumerate(bounding_boxes) if scores[pair[0]] > 0.5]
    store_bounding_boxes(img_name, confident_boxes, gradient, cache)

def faces_present(dets, scores, threshold):
    """returns true if the face detector found at 
    least one face in the image with a score of
    more than 'threshold'."""
    return dets and max(scores) > threshold

def extract_faces_from_image(img_name, cache, threshold=0.5):
    img = io.imread(img_name)
    dets, scores, idx = cache['detector'].run(img, 1)
    if faces_present(dets, scores, threshold):
        extract_confident_detections(img, img_name, dets, scores, cache)

def extract_face_frames(root_path, stage_id):
    paths = get_paths(root_path, stage_id)
    cache = load_cache(paths)
    root, jpgs = get_jpgs_in_dir(paths['tete'])
    img_names = [root + jpg for jpg in jpgs]
    for img_name in tqdm(img_names):
        extract_faces_from_image(img_name, cache)
    save_meta_data(paths)
