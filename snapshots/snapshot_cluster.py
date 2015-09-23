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

def get_dar_dimensions(src_video, DAR = (16.0 / 9.0)):
    sar_dimensions = get_frame_dims(src_video)
    dar_dimensions = {'width': sar_dimensions['height'] * DAR, 
                  'height': sar_dimensions['height']}
    return dar_dimensions

def single_snapshots(src_video, dest_dir, stage_id, times, dar_dims):
    """creates a cluster of (cluster_size) snapshots from the video 
    specified by `src_video` at the times specified by times
    and saves them in `dest_dir`."""
    for selected_time in tqdm(times):
        target_dir = get_target_dir(dest_dir, selected_time)
        snapshot(src_video, target_dir, stage_id, time=time, dimensions=dar_dims)
    print('single snapshots taken')

def snapshot_cluster(src_video, dest_dir, stage_id, times, dar_dims, cluster_size, max_offset):
    """creates a cluster of (cluster_size) snapshots from the video 
    specified by `src_video` at the times specified by times
    and saves them in `dest_dir`."""
    for selected_time in tqdm(times):
        target_dir = get_target_dir(dest_dir, selected_time)
        cluster = time_cluster(selected_time, cluster_size, max_offset)
        for time in cluster:
            snapshot(src_video, target_dir, stage_id, time=time, dimensions=dar_dims)
    print 'snapshot clusters taken'

def take_snapshot_every_half_second(src_video, tmp_clusters, target_dir, stage_id, DAR):
    """saves a snapshot of src_video every half second 
    and saves it to the target_dir."""
    DAR = DAR
    dar_dims = get_dar_dimensions(src_video, DAR=DAR)
    times = half_second_formatted_times_in_video(src_video)
    cluster_size = 1
    max_offset = 0
    # for time in times:        
        # snapshot(src_video, target_dir, stage_id, time=time, dimensions=dar_dims)
    snapshot_cluster(src_video, tmp_clusters, stage_id,
            times=times, dar_dims=dar_dims, 
            cluster_size=cluster_size, max_offset=max_offset)
    extract_sharpest_frames(tmp_clusters, target_dir, stage_id, sigma=3)

def take_snapshot_every_second(src_video, tmp_clusters, target_dir, stage_id, DAR):
    """saves a snapshot of src_video every second 
    and saves it to the target_dir."""
    DAR = DAR
    dar_dims = get_dar_dimensions(src_video, DAR=DAR)
    times = formatted_times_in_video(src_video)
    for time in tqdm(times):        
        snapshot(src_video, target_dir, stage_id, time=time, dimensions=dar_dims)
    # snapshot_cluster(src_video, tmp_clusters, stage_id,
    #         times=times, dar_dims=dar_dims, 
    #         cluster_size=cluster_size, max_offset=max_offset)
    # single_snapshots(src_video, tmp_clusters, stage_id,
    #                     times=times, dar_dims=dar_dims)
    # extract_sharpest_frames(tmp_clusters, target_dir, stage_id, sigma=3)