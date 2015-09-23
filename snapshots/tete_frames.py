import os
import shutil
import pickle
from tqdm import *

from camera import Camera
from file_utils import get_img_paths_in_dir
from time_utils import get_time_from_path
from time_utils import get_times_in_interval
from time_utils import get_contiguous_intervals
from snapshot_cluster import take_cluster_snapshots_at_targets

def get_paths(root_path, stage_id):
    """returns all required paths and ensures that 
    the path to the target directory is valid."""
    target_path = root_path + 'tete_frames/' + stage_id + '/'
    if not os.path.exists(target_path):
        os.makedirs(target_path) 

    paths = {}
    paths['target'] = target_path
    paths['log'] = root_path + 'camera_states/' + stage_id + '.pickle'
    paths['precis'] = root_path + 'precis_frames/' + stage_id + '/'
    paths['src_video'] = root_path + 'raw/Stage' + stage_id +'.m4v'
    paths['tmp_clusters'] = root_path + 'tmp_clusters/' + stage_id + '/'
    return paths

def get_tete_images(paths):
    with open(paths['log'], 'rb') as f:
        camera_states_log = pickle.load(f)
    img_names = get_img_paths_in_dir(paths['precis'])
    labeled_imgs = zip(camera_states_log, img_names)
    tete_imgs = [img for (state, img) in labeled_imgs if state == Camera.Tete]
    return tete_imgs   

def get_tete_target_frames(paths, step):
    tete_imgs = get_tete_images(paths)
    times = [get_time_from_path(tete_img) for tete_img in tete_imgs]
    intervals = get_contiguous_intervals(times)
    target_lists = [get_times_in_interval(interval, step) for interval in intervals]
    targets = sum(target_lists, []) # flattens the list
    return targets

# def extract_sharpest_tete_snapshots(tete_img, target_dir):
#     root, img_name = os.path.split(tete_img)
#     target_name = target_dir + img_name
#     print(target_name)
#     # shutil.copy(tete_img, target_name)

def extract_tete_snapshots(root_path, stage_id, step):
    paths = get_paths(root_path, stage_id)
    targets = get_tete_target_frames(paths, step)
    take_cluster_snapshots_at_targets(targets, paths, stage_id)
    # for tete_img in tqdm(tete_imgs):
    #     extract_sharpest_tete_snapshots(tete_img, paths['target'])