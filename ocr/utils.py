import cv2
import numpy as np

SIGN_WIDTH = 52
SIGN_HEIGHT = 18

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

def apply_threshold_to_image(path):
    """apply a uniform threshold to convert the image located at
    `path` to binary.  he binary image is then inverted to help 
    with contour detection."""
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
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

def top_border(img, thickness=5):
    """returns a description of a rectangle that forms
    a thick border along the top of the image."""
    rectangle = {
        'xy': (0,0),
        'width': img.shape[1] - 1,
        'height': int(thickness / 2),
        'fill': False,
        'edgecolor': "#777777",
        'linewidth': thickness
    }
    return rectangle