import os
import sys
import numpy as np

from tqdm import *
from file_utils import get_target_dir
from time_utils import time_cluster 
from time_utils import get_num_frames
from time_utils import formatted_times_in_video
from snapshot_utils import get_dar_dimensions
from snapshot_utils import get_frame_dims
from snapshot_utils import snapshot
from sharpness_rank import extract_sharpest_frames

def snapshot_cluster(targets, paths, stage_id, dar_dims):
    """creates a cluster of (cluster_size) snapshots from the video 
    specified by `src_video` at the times specified by times
    and saves them in `dest_dir`."""
    cluster_size = 5
    max_offset = 200
    for selected_time in tqdm(targets):
        target_dir = get_target_dir(paths['tmp_clusters'], selected_time)
        cluster = time_cluster(selected_time, cluster_size, max_offset)
        for time in cluster:
            snapshot(paths['src_video'], target_dir, 
                    stage_id, time=time, dimensions=dar_dims)

def take_cluster_snapshots_at_targets(targets, paths, stage_id, DAR = (16.0 / 9.0)):
    """takes a cluster of snapshot of src_video every target 
    and saves it to the target_dir."""
    dar_dims = get_dar_dimensions(paths['src_video'], DAR=DAR)
    snapshot_cluster(targets=targets, paths=paths, stage_id=stage_id, dar_dims=dar_dims)
    extract_sharpest_frames(paths['tmp_clusters'], paths['target'],stage_id)