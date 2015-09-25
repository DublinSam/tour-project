import os
import matplotlib
from skimage import io
from image_utils import crop_frame
from gradients import find_gradient
from digit_classifier import find_number

def get_target_dir(target_dir):
    """ensures that target_dir exists"""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir

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

def save_labeled_face(img_name, img, i, box, gradient, dest_dir):
    """Saves face `i` in `img` with a new filename that 
    includes the gradient at which the snapshot was taken."""
    face_img = crop_frame(img, box)
    face_dims = face_img.shape
    head, tail = os.path.split(img_name)
    face_name = tail[:-4] + ':' + str(i) + ':' + str(gradient) + '.jpg'
    if face_dims[0] > 10 and face_dims[1] > 10:
        matplotlib.image.imsave(dest_dir + face_name, face_img)

def extract_confident_detections(img, img_name, stage_id, dets, scores, model, dest_dir):
    """For the given image, the gradient is calculated and
    passed to 'save_labeled_face()' for detections 
    that meet the required score threshold."""
    distance_to_go = find_number(img_name, model)
    gradient = find_gradient(stage_id, distance_to_go)
    bounding_boxes = get_bounding_boxes(dets)
    for i, box in enumerate(bounding_boxes):
            if scores[i] > 0.5:
                save_labeled_face(img_name, img, i, box, gradient, dest_dir)

def faces_present(dets, scores, threshold):
    """returns true if the face detector found at 
    least one face in the image with a score of
    more than 'threshold'."""
    return dets and max(scores) > threshold

def extract_faces_from_image(img_name, dest_dir, stage_id, model, detector, threshold=0.5):
    img = io.imread(img_name)
    dest_dir = get_target_dir(dest_dir)
    dets, scores, idx = detector.run(img, 1)
    if faces_present(dets, scores, threshold):
        extract_confident_detections(img, img_name, stage_id, dets, scores, model, dest_dir)
