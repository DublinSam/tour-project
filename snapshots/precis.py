import os
import sys
import numpy as np

from tqdm import *
from file_utils import get_target_dir
from time_utils import formatted_times_in_video
from snapshot_utils import get_dar_dimensions
from snapshot_utils import snapshot

def take_precis_snapshots(src_video, target_dir, stage_id, DAR):
    """saves a snapshot of src_video every second 
    and saves it to the target_dir."""
    DAR = DAR
    dar_dims = get_dar_dimensions(src_video, DAR=DAR)
    times = formatted_times_in_video(src_video)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for time in tqdm(times):        
        snapshot(src_video, target_dir, stage_id, time=time, dimensions=dar_dims)