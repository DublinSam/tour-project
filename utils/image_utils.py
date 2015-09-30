from __future__ import division

import os
import cv2
import numpy as np
import scipy.ndimage as ndimage


SIGN_WIDTH = 52
SIGN_HEIGHT = 18

def apply_threshold_to_image(path):
    """apply a uniform threshold to convert the image located at
    `path` to binary.  he binary image is then inverted to help 
    with contour detection."""
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = ndimage.gaussian_filter(img, sigma=1)
    ret, binary_img = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY)
    binary_img = np.invert(binary_img)
    return binary_img    

def find_contours(binary_img):
    """retruns a list of contours (without hierarchical relationships)
    found within the thresholded binary image."""  
    contours, hierarchy = cv2.findContours(image=binary_img, 
                                       mode=cv2.RETR_LIST, 
                                       method=cv2.CHAIN_APPROX_SIMPLE)
    return contours

def crop_frame(frame, crop_region):
    """returns cropped frame using the values specified by
     'crop_region'."""
    tl_x = crop_region['top_left_x'] 
    tl_y = crop_region['top_left_y']
    br_x = crop_region['bottom_right_x']
    br_y = crop_region['bottom_right_y']
    return frame[tl_y:br_y, tl_x:br_x]

def crop_to_scaled_region(img, x_min_scale=0.05, y_min_scale=0.05, 
                 x_max_scale=0.15, y_max_scale=0.1):
    """crops img to the region specified by the scale 
    parameters."""
    rows, cols = img.shape
    x_min, y_min = cols * x_min_scale, rows * y_min_scale
    x_max, y_max = cols * x_max_scale, rows * y_max_scale
    cropped_img = img[y_min:y_max, x_min:x_max]
    return cropped_img

def get_fig_dimensions(width, height):
    """return normalized fig dimensions"""
    aspect_ratio = width / height
    fig_height = 1
    fig_width = aspect_ratio * fig_height
    return (fig_width, fig_height)

def border_rectangle(img, thickness=5):
    """returns a description of a rectangle that forms the 
    grey border around the cropped image (helps with accurately 
    finding contours)"""
    rectangle = {
        'xy': (0,0),
        'width': img.shape[1] - 1,
        'height': img.shape[0] - 1,
        'fill': False,
        'edgecolor': "#777777",
        'linewidth': thickness
    }
    return rectangle

def top_border(img, thickness=10):
    """returns a description of a rectangle that forms
    a thick border along the top of the image."""
    rectangle = {
        'xy': (0,0),
        'width': img.shape[1] - 1,
        'height': 1,
        'fill': False,
        'edgecolor': "#777777",
        'linewidth': thickness
    }
    return rectangle

def white_divider(img, thickness=10):
    """returns a description of a rectangle that forms the 
    grey border around the cropped image (helps with accurately 
    finding contours)"""
    rectangle = {
        'xy': (35,0),
        'width': 1,
        'height': img.shape[0] - 1,
        'fill': False,
        'edgecolor': "#777777",
        'linewidth': thickness
    }
    return rectangle

def bottom_half(img):
    """returns the bounding vertices of a rectangular 
    crop frame that encompasses the lower half of
    the image."""
    dims = img.shape
    center_row = int(dims[0] / 2)
    quadrant_location = {
        'top_left_x': 0,
        'top_left_y': center_row,
        'bottom_right_x': dims[1],
        'bottom_right_y': dims[0]
    }
    return quadrant_location

def bottom_left_quadrant(img):
    """returns the bounding vertices of a rectangular 
    crop frame that encompasses the lower left quadrant of
    the image."""
    dims = img.shape
    center_row = int(dims[0] / 2)
    center_col = int(dims[1] / 2)
    quadrant_location = {
        'top_left_x': 0,
        'top_left_y': center_row,
        'bottom_right_x': center_col,
        'bottom_right_y': dims[0]
    }
    return quadrant_location
