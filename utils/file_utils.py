import os

def get_paths(root_path, stage_id):
    """returns all required paths and ensures that 
    the path to each defirectory is valid."""
    paths = {}
    stage_str = str(stage_id)
    paths['tete'] = root_path + 'tete_frames/' + stage_str + '/'
    paths['log'] = root_path + 'camera_states/' + stage_str + '.pickle'
    paths['precis'] = root_path + 'precis_frames/' + stage_str + '/'
    paths['src_video'] = root_path + 'raw/Stage' + stage_str +'.m4v'
    paths['tmp_clusters'] = root_path + 'tmp_clusters/' + stage_str + '/'
    paths['templates'] = root_path + 'templates/'
    paths['fused'] = root_path + 'ocr/data/fused/'
    paths['digit_model'] = root_path + 'ocr/data/model/'
    paths['test_figures'] = root_path + 'ocr/data/test_figures/'
    paths['digit_training_frames'] = root_path + 'ocr/data/digit_training_frames/'
    paths['strava'] = root_path + 'gradient_data/raw/'
    
    directories = ['tete', 'precis', 'tmp_clusters', 'templates', 'fused', 
                   'digit_model', 'test_figures', 'digit_training_frames']
    for key in directories:
        if not os.path.exists(paths[key]):
            os.makedirs(paths[key]) 
    return paths



def get_jpgs_in_dir(image_dir):
    """returns list of the .jpg files in the given
    directory, together with the root path."""
    frames = []
    root = None
    for root, dirs, fnames in os.walk(image_dir):
        for fname in fnames:
            if is_img_name(fname):
                frames.append(fname)
        root = root
    return root, frames

def get_img_paths_in_dir(image_dir):
    """returns a list of full paths to .jpg files in 
    the given directory."""
    root, frames = get_jpgs_in_dir(image_dir)
    img_paths = [root + frame for frame in frames]
    return img_paths

def is_img_name(fname):
    """returns true if the file is a jpg and ignores
    hidden files sometimes created on ubuntu"""
    return fname.endswith('.jpg') and not fname[::-1].endswith('_.')



def get_target_dir(path, selected_time):
    target_dir = path + selected_time + '/'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir