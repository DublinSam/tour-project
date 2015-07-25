import cv2
import numpy as np

# Hardcoded values for the location of the 'km to go' sign
# (that need to be updated for each new piece of footage)
CROP_FRAME = {
    'top_left_x': 169,
    'top_left_y': 23,
    'bottom_right_x': 217,
    'bottom_right_y': 39
}

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

def crop_frame(frame):
    """returns cropped frame using the values provided at
     the top of the file."""
    tl_x = CROP_FRAME['top_left_x'] 
    tl_y = CROP_FRAME['top_left_y']
    br_x = CROP_FRAME['bottom_right_x']
    br_y = CROP_FRAME['bottom_right_y']
    return frame[tl_y:br_y, tl_x:br_x]

def get_fig_dimensions():
    """Hardcoded dimensions based on CROP_FRAME values"""
    width = CROP_FRAME['bottom_right_x'] - CROP_FRAME['top_left_x']
    height = CROP_FRAME['bottom_right_y'] - CROP_FRAME['top_left_y']
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