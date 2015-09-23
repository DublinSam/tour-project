import string
import subprocess

def snapshot(input, output, stage_id, time, dimensions):
    """takes snapshots of the video specified by input 
    at the given frequency and stores them as jpg's in 
    'output_dir'"""
    time = ffmpeg_format_time(time)
    snap_ps = subprocess.call(("ffmpeg", 
                                "-ss", time,
    #not valid for ubuntu server                            "-noaccurate_seek",
                                "-i", input,
    #not valid for ubuntu server                            "-filter:v",
                                "-vf",
                                "scale=" + str(dimensions['width']) 
                                + ':' + str(dimensions['height']), 
                                "-qscale:v", "2", # best jpeg quality possible
                                "-vframes", "1",
                                output + stage_id + '-' + time[0:2] + '_' + time[3:] + '.jpg'))

def get_frame_dims(input):
    """return the frame dimensions of the video specified 
    by input.  
    ---------
    NOTE: This returns the dimensions of the 
    stored video, not necessarily how it is supposed to be
    viewed (look up Storage Aspect Ratio vs Display Aspect
    Ratio for more details)."""
    data_ps = subprocess.Popen(("ffprobe", "-v", "quiet",
    #not valid for ubuntu server       "-print_format", "json",
                                "-show_streams",
                                input),
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT)
    data_msg = subprocess.check_output(('grep', 'height\|width'), 
                                    stdin=data_ps.stdout)
    msg = clean_msg(data_msg)
    #not valid for ubuntu server  dims = msg[:-1].split(',') # remove trailing comma before splitting
    split_index = msg.index('height')
    dims = [msg[:split_index], msg[split_index:]]
    dims = [int(dim.split('=')[1]) for dim in dims]
    dimensions = {'width': dims[0],
                  'height': dims[1]}
    return dimensions

def ffmpeg_format_time(time):
    """To work with ffmpeg, we must convert time 
    formats from HH:MM:SS:MMM to HH:MM:SS.MMM
    (the last period is only necesssary for this stage)."""
    ffmpeg_time = time[:8] + '.' + time[9:]
    return ffmpeg_time

def get_dar_dimensions(src_video, DAR = (16.0 / 9.0)):
    sar_dimensions = get_frame_dims(src_video)
    dar_dimensions = {'width': sar_dimensions['height'] * DAR, 
                  'height': sar_dimensions['height']}
    return dar_dimensions


def clean_msg(msg):
    """cleans up messages by removing whitespace
    and newline characters."""
    msg = msg.replace(' ', '')
    msg = msg.replace('\n', '')
    return msg
