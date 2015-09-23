import os
import subprocess
import numpy as np

def get_time_from_img_path(path):
    """extract the formatted time from a full
    image path of the form /a/b/c/d/.../HH:MM:SS.jpg"""
    formatted_time = os.path.split(path)[1][:-4]
    return formatted_time

def get_num_frames(duration, fps):
    """returns the total number of frames contained
    in a video with the duration specified as a string
    HH:MM:SS"""
    seconds = time_to_seconds(duration)
    num_frames = seconds * fps
    return num_frames

def get_video_duration(path):
    """returns duration of the video specified by `path`
    as a string in the format HH:MM:SS"""
    ffmpeg_ps = subprocess.Popen(("ffmpeg", "-i", path),
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT)
    output = subprocess.check_output(('grep', 'Duration'), 
                                    stdin=ffmpeg_ps.stdout)
    duration = output[12:20]
    return duration

def formatted_times_in_video(src_video):
    """returns a list of each second of video footage
    formatted in the form 'HH:MM:SS'"""
    duration = get_video_duration(src_video)
    seconds = time_to_seconds(duration)
    times = [seconds_to_time(second) for second in range(seconds)]
    return times

def time_to_seconds(duration):
    """returns the total number of seconds in a 
    duration of the format HH:MM:SS"""
    hours = int(duration[:2])
    mins = int(duration[3:5])
    seconds = int(duration[6:8]) + (60 * mins) + (60 * 60 * hours)
    return seconds

def seconds_to_time(num_seconds):
    """returns a duration in the format HH:MM:SS
    produced from the given number of seconds"""
    hours = int(num_seconds / 3600)
    hour_seconds = hours * 3600
    mins = int((num_seconds - hour_seconds) / 60)
    min_seconds = mins * 60
    seconds = num_seconds - hour_seconds - min_seconds
    time = digit_string(hours) + ":" + digit_string(mins) + ":" + digit_string(seconds)
    return time

def parse_hours(formatted_time):
    """takes a string of the form HH:MM:SS or HH:MM:SS.MMM 
    and returns the string HH"""
    return int(formatted_time[:2])

def parse_mins(formatted_time):
    """takes a string of the form HH:MM:SS or HH:MM:SS.MMM 
    and returns the string MM"""
    return int(formatted_time[3:5])

def parse_seconds(formatted_time):
    """takes a string of the form HH:MM:SS or HH:MM:SS.MMM 
    and returns the string SS"""
    return int(formatted_time[6:8])

def format_time(hours, mins, seconds, milliseconds=None):
    """takes in a set of integers representing the time and 
    composes a string in the format HH:MM:SS, or if a 
    millisecond argument is supplied, returns a string 
    in the format HH:MM:SS.MMM."""
    hours = str(ensure_two_digits(hours))
    mins = str(ensure_two_digits(mins))
    seconds = str(ensure_two_digits(seconds))
    formatted_time =  hours + ':' + mins + ':' + str(seconds)
    if milliseconds:
        milliseconds = str(ensure_three_digits(milliseconds))
        formatted_time = formatted_time + ':' + milliseconds
    return formatted_time


def offset_time(time, offset):
    """takes a time in the format 'HH:MM:SS' and a millisecond
    offset between -999 and 999 and returns a formatted time 
    in the form `HH:MM:SS:mmm` where H = hours, M = minutes, 
    S = seconds, m = milliseconds"""
    if offset >= 0:
        offset = ensure_three_digits(offset)
        formatted_time =  time + ':' + str(offset)
    else:
        hours = parse_hours(time)
        mins = parse_mins(time)
        seconds = parse_seconds(time) - 1
        milliseconds = 1000 + offset
        formatted_time =  format_time(hours, mins, seconds, milliseconds)
    return formatted_time

def time_cluster(time, size=5, max_offset=200):
    offsets = np.linspace(-max_offset, max_offset, size)
    cluster = [offset_time(time, int(offset)) for offset in offsets]
    return cluster

def ensure_two_digits(num):
    """takes an int `num` between 0 and 99 returns a number 
    between 00 and 09 as a string that has two digits (i.e.
    returns '20' rather than '2')"""
    if 10 <= num <= 99:
        two_digit_num = str(num)
    else:
        two_digit_num = '0' + str(num)
    return two_digit_num

def digit_string(num):
    """returns string form of num in the form NN, 
    where numbers less than 10, for instance 6, 
    becomes '06'"""
    digit_string = str(num)
    if num < 10:
        digit_string = "0" + digit_string
    return digit_string

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

def half_second_formatted_times_in_video(src_video):
    """returns a list of each second of video footage
    formatted in the form 'HH:MM:SS:S where the last S 
    stands for split seconds, and take the value 0 or 5."""
    duration = get_video_duration(src_video)
    seconds = time_to_seconds(duration)
    times = [seconds_to_time(second) for second in range(seconds)]
    second_intervals = [time + ':000' for time in times]
    half_second_intervals = [time + ':500' for time in times]
    all_times = second_intervals + half_second_intervals
    return sorted(all_times)