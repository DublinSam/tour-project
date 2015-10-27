import string
import sys
import subprocess


from time_utils import parse_hours, parse_mins
from time_utils import parse_seconds, parse_milliseconds

def snapshot(input, output, stage_id, time, dimensions):
    """takes snapshots of the video specified by input 
    at the given frequency and stores them as jpg's in 
    'output_dir'"""
    ffmpeg_time = ffmpeg_format_time(time)
    snap_ps = subprocess.call(("ffmpeg", 
                                "-ss", ffmpeg_time,
                                "-noaccurate_seek",
				"-threads", "1", # (cluster only runs single threaded)
                                "-i", input,
                                "-filter:v",
                                "scale=" + str(dimensions['width']) 
                                + ':' + str(dimensions['height']), 
                                "-qscale:v", "2", # best jpeg quality possible
                                "-vframes", "1",
                                "".join((output, stage_id, '-',
                                       standard_format_time(ffmpeg_time), '.jpg'))))


def get_frame_dims(input):
    """return the frame dimensions of the video specified 
    by input.  
    ---------
    NOTE: This returns the dimensions of the 
    stored video, not necessarily how it is supposed to be
    viewed (look up Storage Aspect Ratio vs Display Aspect
    Ratio for more details)."""
    data_ps = subprocess.Popen(("ffprobe", "-v", "quiet",
                                "-print_format", "json",
                                "-show_streams",
                                input),
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT)
    data_msg = subprocess.check_output(('grep', 'height\|width'), 
                                    stdin=data_ps.stdout)
    msg = clean_msg(data_msg)
    dims = msg[:-1].split(',') # remove trailing comma before splitting
    dims = [int(dim.split(':')[1]) for dim in dims]
    dimensions = {'width': dims[0],
                  'height': dims[1]}
    print('sar dimensions', dimensions)
    return dimensions

def ffmpeg_format_time(time):
    """To work with ffmpeg, we must convert time 
    formats from HH:MM:SS:MMM to HH:MM:SS.MMM
    (the last period is only necesssary for this stage)."""
    ffmpeg_time = time[:8] + '.' + time[9:]
    return ffmpeg_time

def standard_format_time(ffmpeg_time):
    """Takes a time in ffmpeg format HH:MM:SS.MMM
    and returns it to the standard format HH:MM:SS:MMM"""
    time = ffmpeg_time[:8] + ':' + ffmpeg_time[9:]
    return time


def get_dar_dimensions(src_video, DAR = (16.0 / 9.0)):
    sar_dimensions = get_frame_dims(src_video)
    dar_dimensions = {'width': sar_dimensions['height'] * DAR, 
                  'height': sar_dimensions['height']}
    print('dar dimensions', dar_dimensions)
    return dar_dimensions

def clean_msg(msg):
    """cleans up messages by removing whitespace
    and newline characters."""
    msg = msg.replace(' ', '')
    msg = msg.replace('\n', '')
    return msg
