import os
import cv2
import math
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from collections import Counter

from utils import crop_frame
from utils import top_border
from utils import find_contours
from utils import get_jpgs_in_dir
from utils import border_rectangle
from utils import get_fig_dimensions
from utils import apply_threshold_to_image
from utils import SIGN_WIDTH, SIGN_HEIGHT

from distance_labels import digit_region

# Path to data (sample frames from sports footage)
DATA_PATH = '/Users/samuelalbanie/aims_course/project_two/code/tour_data/project_tools/ocr/data'

# Location of sample images used to train digit classifier
SAMPLE_IMAGES = DATA_PATH + '/training_images/'

# Location where the fused training image will be stored
TARGET_DIR = DATA_PATH + '/fused_image/'

# Location where the model will be stored
MODEL_DIR = DATA_PATH + '/model/'

def count_digits(file_list):
    """counts the instances of digits occuring 
    in the file names present in file_list"""
    counter = Counter(file_list)
    digits, counts = [],[]
    for digit in sorted(counter):
        digits.append(digit)
        counts.append(counter[digit])
    return (digits, counts)

def plot_histogram_of_digits(file_list):
    """generates a histogram of the digits 
    found in file_list."""
    digits, counts = count_digits(file_list)
    indexes = np.arange(len(digits))    
    plt.bar(indexes, counts, alpha=0.6)
    plt.title('Distribution of training digits')
    plt.xlabel('digit')
    plt.ylabel('counts')
    plt.xticks(indexes +  0.5, digits)
    plt.show()

def show_training_digits_distribution(src_dir):
    """displays a histogram of the counts of 
    digits from the training data in src_dir"""
    path, jpgs = get_jpgs_in_dir(src_dir)
    file_list = "".join([img_name[:-4] for img_name in jpgs])
    plot_histogram_of_digits(file_list)

def get_subplots(num_rows, num_cols):
    """returns a tuple (fig, axes) for producing subplots
    of the given numbers of rows and columns"""
    fig, axes = plt.subplots(num_rows, num_cols)
    fig_width, fig_height = get_fig_dimensions(SIGN_WIDTH, SIGN_HEIGHT)
    fig.set_size_inches(fig_width * num_cols, fig_height * num_rows)
    fig.subplots_adjust(hspace=0, wspace=0)
    axes = [ax[0] for ax in axes.reshape(-1,1)]
    plt.axis('off')
    return (fig, axes)

def construct_training_image(src_dir, target_dir, num_cols=3):
    """constructs an image containing at least one example of 
    each digit based on the files in src_dir and saves it as 
    'digit_examples.jpg' in target_dir. Saving the image isn't 
    necessary, but it provides a useful sanity check."""
    root, frame_paths = get_jpgs_in_dir(src_dir)
    templates = get_templates()
    num_rows = int(math.ceil(len(frame_paths) / num_cols))
    fig, axes = get_subplots(num_rows, num_cols)
    
    for frame, ax in zip(frame_paths, axes):
        img = cv2.imread(root + frame, cv2.IMREAD_GRAYSCALE)
        km_img = digit_region(img, templates['flag'])
        rectangle = border_rectangle(km_img)
        top = top_border(km_img)
        ax.imshow(km_img, cmap = plt.cm.Greys_r)
        ax.add_patch(patches.Rectangle(**rectangle))
        ax.add_patch(patches.Rectangle(**top))
        ax.set_axis_off()
    plt.savefig(target_dir + 'digit_examples.jpg', bbox_inches='tight', pad_inches=0)

def manually_label_digits(src_dir):
    """returns a tuple containing:
    'samples':  a list of shrunk digit images 
    'responses': a list of the label values (each a digit)"""
    samples = np.empty((0,400))
    responses = [] # store the labels
    keys = [i for i in range(48,58)]
    img_path = src_dir + 'digit_examples.jpg'
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

def save_model_labels(src_dir):
    samples, responses = manually_label_digits(src_dir)
    cv2.destroyAllWindows()
    responses = np.array(responses,np.float32)
    responses = responses.reshape((responses.size,1))
    print("labelling complete")
    np.savetxt(MODEL_DIR + 'tdf_digit_samples.data',samples)
    np.savetxt(MODEL_DIR + 'tdf_digit_responses.data',responses)