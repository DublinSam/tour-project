import cv2

from image_utils import crop_frame 
from image_utils import bottom_left_quadrant


PATH = '/Users/samuelalbanie/aims_course/project_two/code/DVD/'
TEMPLATE_PATH = PATH + 'templates/'
FLAG_PATH = TEMPLATE_PATH + 'flag.jpg'
BREAKAWAY_PATH = TEMPLATE_PATH + 'breakaway.jpg'
TETE_PATH = TEMPLATE_PATH + 'tete.jpg'
GROUP2_PATH = TEMPLATE_PATH + 'group2.jpg'
GROUP3_PATH = TEMPLATE_PATH + 'group3.jpg'
GROUP4_PATH = TEMPLATE_PATH + 'group4.jpg'
ARRIERE_PATH = TEMPLATE_PATH + 'arriere.jpg'
KM_PATH = TEMPLATE_PATH + 'km_sign.jpg'

# Confidence threshold for template matching to be considered
# valid
CONFIDENCE = 0.8
# Define the width and height of the 'km to go' sign 
SIGN_WIDTH = 200
SIGN_HEIGHT = 20

def contains_template(img, template, confidence):
    """returns true if the template matching achieves the 
    given level of confidence in locating the template.
    Otherwise returns false."""
    max_val,_ = best_match(img, template)
    return max_val > confidence

def get_templates(km_path=KM_PATH, 
                  
                  flag_path=FLAG_PATH, 
                  breakaway_path=BREAKAWAY_PATH,
                  tete_path=TETE_PATH,
                  group2_path=GROUP2_PATH,
                  group3_path=GROUP3_PATH,
                  group4_path=GROUP4_PATH,
                  arriere_path=ARRIERE_PATH,
                  ):
    """returns the templates at the given paths. This is 
    done for caching purposes."""
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

def contains_breakaway_template(img, templates, confidence=CONFIDENCE):
    extended_sign_width = SIGN_WIDTH + 20
    sign_location = find_sign_location(img, templates['flag'], width=extended_sign_width)
    cropped_img = crop_frame(img, sign_location)
    has_breakaway = contains_template(cropped_img, templates['breakaway'], confidence)
    return has_breakaway

def contains_tete_template(img, templates, confidence=CONFIDENCE):
    quadrant = bottom_left_quadrant(img)
    cropped_img = crop_frame(img, quadrant)
    is_tete = contains_template(cropped_img, templates['tete'], confidence)
    return is_tete

def contains_poursuivants_template(img, templates, confidence=CONFIDENCE):
    quadrant = bottom_left_quadrant(img)
    cropped_img = crop_frame(img, quadrant)
    is_group2 = contains_template(cropped_img, templates['group2'], confidence)
    is_group3 = contains_template(cropped_img, templates['group3'], confidence)
    is_group4 = contains_template(cropped_img, templates['group4'], confidence)
    is_arriere = contains_template(cropped_img, templates['arriere'], confidence)
    return is_group2 or is_group3 or is_group4 or is_arriere

def digit_region(img, region_width=52):
    """returns the region of the image containg the digits
    representing the distance to go. The img must contain 
    the 'km to go' sign."""
    templates = get_templates()
    sign_frame = crop_to_sign_using_template(img, templates['flag'])
    score, loc = best_match(sign_frame, templates['km'])
    region_width = 52
    digit_location = {'top_left_x': loc[0] - region_width,
                      'top_left_y': 0,
                      'bottom_right_x': loc[0],
                      'bottom_right_y': loc[1] + templates['km'].shape[0]}
    digits_frame = crop_frame(sign_frame, digit_location)
    return digits_frame