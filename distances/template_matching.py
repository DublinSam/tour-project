import cv2
from file_utils import get_paths
from image_utils import crop_frame 
from image_utils import bottom_half
from image_utils import bottom_left_quadrant

# Confidence threshold for template matching to be considered
# valid
CONFIDENCE = 0.8
# Define the width and height of the 'km to go' sign 
SIGN_WIDTH = 200
SIGN_HEIGHT = 20

def contains_template(img, template, confidence):
    """returns true if the template mat1ching achieves the 
    given level of confidence in locating the template.
    Otherwise returns false."""
    max_val,_ = best_match(img, template)
    return max_val > confidence

def get_templates(paths):
    """returns the templates at the given paths. This is 
    done for caching purposes."""
    flag_path = paths['templates'] + 'flag.jpg'
    breakaway_path = paths['templates'] + 'breakaway.jpg'
    tete_path = paths['templates'] + 'tete.jpg'
    group2_path = paths['templates'] + 'group2.jpg'
    group3_path = paths['templates'] + 'group3.jpg'
    group4_path = paths['templates'] + 'group4.jpg'
    arriere_path = paths['templates'] + 'arriere.jpg'
    km_path = paths['templates'] + 'km_sign.jpg'

    flag_template = cv2.imread(flag_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    km_template = cv2.imread(km_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    breakaway_template = cv2.imread(breakaway_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    tete_template = cv2.imread(tete_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    group2_template = cv2.imread(group2_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    group3_template = cv2.imread(group3_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    group4_template = cv2.imread(group4_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    arriere_template = cv2.imread(arriere_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    templates = {'km': km_template, 
                 'flag': flag_template, 
                 'breakaway': breakaway_template,
                 'tete':tete_template,
                 'group2':group2_template,
                 'group3':group3_template,
                 'group4':group4_template,
                 'arriere':arriere_template,
                 }
    return templates

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

def crop_to_sign_using_template(img, flag_template):
    """returns a cropped frame containing just the 
    'km to go sign'"""
    sign_location = find_sign_location(img, flag_template)
    cropped_frame = crop_frame(img, sign_location)
    return cropped_frame

def contains_chequered_flag(img, template, confidence=CONFIDENCE):
    """returns true if the image contains a chequered 
    flag in SIGN_REGION"""
    has_flag = contains_template(img, template, confidence)
    return has_flag

def is_distance_measured_in_km(img, templates, confidence=CONFIDENCE):
    """returns true if the distance on the 'to go' sign is 
    measured in km (i.e. it contains the 'km' template)."""
    sign_location = find_sign_location(img, templates['flag'])
    cropped_img = crop_frame(img, sign_location)
    in_km = contains_template(cropped_img, templates['km'], confidence)
    return in_km

def contains_tete_template(img, templates, confidence=CONFIDENCE):
    quadrant = bottom_left_quadrant(img)
    cropped_img = crop_frame(img, quadrant)
    is_tete = contains_template(cropped_img, templates['tete'], confidence)
    return is_tete

def contains_group_positions(img, templates, confidence=CONFIDENCE):
    """returns true if the screen is annotated with a complete ranking of the 
    time gaps between the first three groups."""
    half = bottom_half(img)
    cropped_img = crop_frame(img, half)
    is_tete = contains_template(cropped_img, templates['tete'], confidence)
    is_group2 = contains_template(cropped_img, templates['group2'], confidence)
    is_group3 = contains_template(cropped_img, templates['group3'], confidence)
    return is_tete and is_group2 and is_group3

def contains_poursuivants_template(img, templates, confidence=CONFIDENCE):
    quadrant = bottom_left_quadrant(img)
    cropped_img = crop_frame(img, quadrant)
    is_group2 = contains_template(cropped_img, templates['group2'], confidence)
    is_group3 = contains_template(cropped_img, templates['group3'], confidence)
    is_group4 = contains_template(cropped_img, templates['group4'], confidence)
    is_arriere = contains_template(cropped_img, templates['arriere'], confidence)
    return is_group2 or is_group3 or is_group4 or is_arriere

def digit_region(img, templates, region_width=52):
    """returns the region of the image containg the digits
    representing the distance to go. The img must contain 
    the 'km to go' sign."""
    sign_frame = crop_to_sign_using_template(img, templates['flag'])
    score, loc = best_match(sign_frame, templates['km'])
    region_width = 52
    digit_location = {'top_left_x': loc[0] - region_width,
                      'top_left_y': 0,
                      'bottom_right_x': loc[0],
                      'bottom_right_y': loc[1] + templates['km'].shape[0]}
    digits_frame = crop_frame(sign_frame, digit_location)
    return digits_frame