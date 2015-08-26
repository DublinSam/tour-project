import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from collections import Counter

from utils import crop_frame
from utils import find_contours
from utils import border_rectangle
from utils import get_fig_dimensions
from utils import apply_threshold_to_image
from distance_labels import find_sign_location

# Path to data (sample frames from sports footage)
DATA_PATH = '/Users/samuelalbanie/aims_course/project_two/code/tour_data/project_tools/ocr/data'

# Location of sample images used to train digit classifier
SAMPLE_IMAGES = DATA_PATH + '/training_images/'

# Location where the fused training image will be stored
TARGET_DIR = DATA_PATH + '/fused_image/'

# Location where the model will be stored
MODEL_DIR = DATA_PATH + '/model/'

def get_jpgs_in_dir(image_dir):
    """returns list of the .jpg files in the given
    directory, together with the root path."""
    frames = []
    root = None
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith('.jpg'):
                frames.append(file)
        root = root
    return root, frames

def show_training_digits_distribution(src_dir):
    path, jpgs = get_jpgs_in_dir(src_dir)
    file_list = "".join([img_name[:-4] for img_name in jpgs])
    counter = Counter(file_list)
    digits, counts = [],[]
    for digit in sorted(counter):
        digits.append(digit)
        counts.append(counter[digit])

    indexes = np.arange(len(digits))
    width = 1
    plt.bar(indexes, counts, alpha=0.6)
    plt.title('Distribution of training digits')
    plt.xlabel('digit')
    plt.ylabel('counts')
    plt.xticks(indexes + width * 0.5, digits)
    plt.show()

def construct_training_image(src_dir, target_dir, template, sign_region, sign_width, sign_height):
    """constructs an image containing at least one example of 
    each digit based on the files in src_dir and saves it as 
    'digit_examples.jpg' in target_dir.  The digits are found in 
    the region specified by sign_region. Saving the image isn't 
    necessary, but it provides a useful sanity check."""
    root, frame_paths = get_jpgs_in_dir(src_dir)

    # Set up pyplot figure to draw sample digits onto
    fig, axes = plt.subplots(len(frame_paths),1)
    fig_width, fig_height = get_fig_dimensions(sign_width, sign_height)
    fig.set_size_inches(fig_width, len(frame_paths) * fig_height)
    fig.subplots_adjust(hspace=0, wspace=0)
    plt.axis('off')

    for frame, ax in zip(frame_paths, axes):
        img = cv2.imread(root + frame, cv2.IMREAD_GRAYSCALE)
        crop_region = find_sign_location(root + frame, template, sign_region, sign_width, sign_height)
        km_img = crop_frame(img, crop_region)
        rectangle = border_rectangle(km_img)
        ax.imshow(km_img, cmap = plt.cm.Greys_r)
        ax.add_patch(patches.Rectangle(**rectangle))
        ax.set_axis_off()
    
    plt.savefig(target_dir + 'digit_examples.jpg', bbox_inches='tight', pad_inches=0)

def manually_label_digits():
    """returns a tuple containing:
    'samples':  a list of shrunk digit images 
    'responses': a list of the label values (each a digit)"""
    samples = np.empty((0,400))
    responses = [] # store the labels
    keys = [i for i in range(48,58)]
    img_path = TARGET_DIR + 'digit_examples.jpg'
    binary_img = apply_threshold_to_image(img_path)
    binary_img_copy = np.copy(binary_img)
    contours = find_contours(binary_img)
    for contour in contours:
        if 50 < cv2.contourArea(contour) < 4000:
            [x,y,w,h] = cv2.boundingRect(contour)
            if  h > 25 and w < 60:
                cv2.rectangle(binary_img_copy,(x,y),(x+w,y+h),(0,0,255),2)
                roi = binary_img[y:y+h,x:x+w]
                roi_small = cv2.resize(roi,(20,20))
                cv2.imshow('digit samples', binary_img_copy)
                key = cv2.waitKey(0)

                if key == 27:  # (escape to quit)
                    cv2.destroyAllWindows()
                elif key in keys:
                    responses.append(int(chr(key)))
                    sample = roi_small.reshape((1,400))
                    samples = np.append(samples,sample,0)
    return (samples, responses)

def save_model_labels():
    samples, responses = manually_label_digits()
    cv2.destroyAllWindows()
    responses = np.array(responses,np.float32)
    responses = responses.reshape((responses.size,1))
    print("labelling complete")
    np.savetxt(MODEL_DIR + 'tdf_digit_samples.data',samples)
    np.savetxt(MODEL_DIR + 'tdf_digit_responses.data',responses)