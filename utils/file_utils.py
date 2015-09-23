import os

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

def get_img_paths_in_dir(image_dir):
    """returns a list of full paths to .jpg files in 
    the given directory."""
    root, frames = get_jpgs_in_dir(image_dir)
    img_paths = [root + '/' + frame for frame in frames]
    return img_paths

def get_target_dir(path, selected_time):
    target_dir = path + selected_time[:10] + '/'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir