import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches

from utils import crop_frame
from utils import find_contours
from utils import border_rectangle
from utils import get_fig_dimensions
from utils import apply_threshold_to_image
from train_classifier import DATA_PATH
from train_classifier import MODEL_DIR

TEST_FIGURES = DATA_PATH + '/test_figures/'

def load_model():
    samples = np.loadtxt(MODEL_DIR + 'tdf_digit_samples.data', np.float32)
    responses = np.loadtxt(MODEL_DIR + 'tdf_digit_responses.data', np.float32)
    responses = responses.reshape((responses.size,1))
    model = cv2.KNearest()
    model.train(samples, responses)
    return model

def create_test_fig(km_img, rectangle):
    fig_width, fig_height = get_fig_dimensions()
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(fig_width, fig_height)
    fig.subplots_adjust(hspace=0, wspace=0)
    ax.imshow(km_img, cmap = plt.cm.Greys_r)
    ax.add_patch(patches.Rectangle(**rectangle))
    ax.set_axis_off()
    plt.savefig(TEST_FIGURES + 'current_fig.jpg', bbox_inches='tight', pad_inches=0)

def preprocess(img_path):
    """Crops the original image so that it only contains the 'km to go'
    sign and adds a grey border to help with digit classification. This 
    is saved to file rather than passed around """
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError('Image not found')
    km_img = crop_frame(img)
    rectangle = border_rectangle(km_img)
    create_test_fig(km_img, rectangle)

def classify(img_path, model):
    """Apply kNN with k = 1 to categorize each digit in the image."""
    preprocess(img_path)
    binary_img = apply_threshold_to_image(TEST_FIGURES + 'current_fig.jpg')
    contours = find_contours(binary_img)
    final_contours, final_results = [],[]
    for contour in contours:
        if 50 < cv2.contourArea(contour) < 4000:
            [x, y, w, h] = cv2.boundingRect(contour)
            if h > 25 and w < 50:
                # cv2.rectangle(test_img, (x,y), (x+w, y+h), (255,0,0), 2)
                roi = binary_img[y:y+h, x:x+w]
                roi_small = cv2.resize(roi, (20,20))
                roi_small = roi_small.reshape((1,400))
                roi_small = np.float32(roi_small)
                retval, results, neigh_resp, dists = model.find_nearest(roi_small, k = 1)
                final_contours.append(contour)
                final_results.append(results[0][0])
    return (final_results, final_contours)

def arrange_digits_in_order(digits, contours):
    digit_positions = []
    for contour, digit in zip(contours, digits):
        leftmost = contour[contour[:,:,0].argmin()][0][0]
        digit_positions.append((leftmost, digit))
    sorted_positions = sorted(digit_positions, key=lambda x: x[0])
    return [pair[1] for pair in sorted_positions]

def find_number(img_path, model):
    final_results, final_contours = classify(img_path, model)
    ordered_digits = arrange_digits_in_order(final_results, final_contours)
    total = 0.0    
    for i, digit in enumerate(reversed(ordered_digits)):
        total += digit * 10 ** (i - 1)
    total = round(total,1) # round to one decimal place
    return total