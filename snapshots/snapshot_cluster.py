import os
import sys
import numpy as np

from snapshot_utils import snapshot
from snapshot_utils import get_num_frames
from snapshot_utils import get_frame_dims

# set the path to mp4 file
ROOT_PATH = '/Users/samuelalbanie/aims_course/project_two/code/DVD/'

INPUT_PATH = ROOT_PATH + 'raw/Stage1.m4v'
OUTPUT_PATH = ROOT_PATH + 'frames/'

selected_times = ["17:14", "14:25", "11:36", "18:31"]

def get_dar_dimensions(src_video, DAR = (16.0 / 9.0)):
    sar_dimensions = get_frame_dims(src_video)
    dar_dimensions = {'width': sar_dimensions['height'] * DAR, 
                  'height': sar_dimensions['height']}
    return dar_dimensions


def snapshot_cluster(src_video, dest_dir, stage_id, times, dar_dims, cluster_size, max_offset):
    """creates a cluster of (cluster_size) snapshots from the video 
    specified by `src_video` at the times specified by times
    and saves them in `dest_dir`."""
    for selected_time in times:
        target_dir = get_target_dir(dest_dir, selected_time)
        cluster = time_cluster(selected_time, cluster_size, max_offset)
        for time in cluster:
            snapshot(src_video, target_dir, stage_id, time=time, dimensions=dar_dims)
    print 'snapshot clusters taken'

def get_target_dir(path, selected_time):
    target_dir = path + selected_time[:8] + '/'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir

def time_cluster(time, size=5, max_offset=200):
    offsets = np.linspace(-max_offset, max_offset, size)
    cluster = [offset_time(time, int(offset)) for offset in offsets]
    return cluster

def offset_time(time, offset):
    """takes a time in the format 'MM:SS' and a millisecond
    offset between -999 and 999 and returns a formatted time 
    in the form `MM:SS.mmm` where M = minutes, S = seconds, 
    m = milliseconds"""
    if offset >= 0:
        offset = ensure_three_digits(offset)
        formatted_time =  time + '.' + str(offset)
    else:
        mins = time[:2]
        seconds = int(time[-2:]) - 1
        milliseconds = 1000 + offset
        formatted_time =  mins + ':' + str(seconds) + '.' + str(milliseconds)
    return formatted_time

def ensure_three_digits(num):
    """takes an int `num` between 0 and 999 returns a number 
    between 000 and 999 as a string that has three digits (i.e.
    returns '020' rather than '20')"""
    if 100 <= num <= 999:
        three_digit_num = str(num)
    elif 10 <= num <= 99:
        three_digit_num = '0' + str(num)
    else:
        three_digit_num = '00' + str(num)
    return three_digit_num