import os
import cv2
import shutil
import numpy as np

def extract_sharpest_frames(src_dir, target_dir, stage_id, filter_size=120):
    root = src_dir
    dirnames = next(os.walk(root))[1]
    for dirname in dirnames:
        extract_from_dir(root, dirname, target_dir, stage_id, filter_size)

def extract_from_dir(root, dirname, target_dir, stage_id, filter_size):
    img_names = get_images_in_dir(root, dirname)
    sharpest_img = find_sharpest(img_names, filter_size)
    target_name = target_dir + stage_id + '-' + dirname[:2] + '_' + dirname[3:] + '.jpg'
    shutil.copy(sharpest_img, target_name)

def get_images_in_dir(root, dirname):
    all_files = next(os.walk(root + dirname + '/'))[2]
    imgs = [root + dirname + '/' + fname for fname in all_files if fname.endswith('.jpg')]
    return imgs

def find_sharpest(img_names, filter_size):
    """calculates a 'sharpness' value for the center of each image  
    named in img_names and returns the img with the largest value."""
    sharpness_scores = {}
    for img_name in img_names:
        img = cv2.imread(img_name, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        focused_img = focus_on_center(img, scale=0.7)
        sharpness = calculate_sharpness(focused_img, filter_size)
        sharpness_scores[img_name] = sharpness
    sharpest_img = max(sharpness_scores, key=sharpness_scores.get)
    return sharpest_img

def calculate_sharpness(img, filter_size):
    """returns a 'sharpness' value for the input `img`.
    This is calculated as the sum of the log of the 
    absolute values of the higher frequencies in the 
    image spectrum. The intuition is that sharper images
    should have greater weigthing towards the higher end of
    their spectrum."""
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    upper_spectrum = high_pass_filter(fshift, filter_size)
    log_magnitude = 20 * np.log(np.abs(upper_spectrum))
    sharpness = np.sum(log_magnitude)
    return sharpness

def high_pass_filter(spectrum, filter_size):
    """returns a 2d spectrum with lower_frequencies set to 
    (almost) zero."""
    rows, cols = spectrum.shape
    crow, ccol = rows/2 , cols/2
    spectrum[crow - filter_size:crow + filter_size, 
           ccol - filter_size:ccol + filter_size] = 0.00000001
    return spectrum


def focus_on_center(img, scale=0.7):
    """returns a cropped version of `img`. The cropped image 
    is formed by scaling down the size of `img` (by `scale`) and 
    centering a rectange of this size on the center of `img`."""
    rows, cols = img.shape
    crow, ccol = rows/2 , cols/2
    scaled_width, scaled_height = cols * scale, rows * scale
    img = img[crow - (scaled_height/2):crow + (scaled_height/2), 
              ccol - (scaled_width/2):ccol + (scaled_width/2)] 
    return img