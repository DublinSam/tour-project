import os
import subprocess
import numpy as np

def get_time_from_path(path):
    """extract the formatted time from a full
    image path of the form /a/b/c/d/.../HH:MM:SS.jpg"""
    stage_time = os.path.split(path)[1][:-4]
    formatted_time = stage_time.split('-')[1]
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
    hours = parse_hours(duration)
    mins = parse_mins(duration)
    seconds = parse_seconds(duration) + (60 * mins) + (60 * 60 * hours)
    return seconds

def seconds_to_time(num_seconds):
    """returns a duration in the format HH:MM:SS:MMM
    produced from the given number of seconds"""
    hours = int(num_seconds / 3600)
    hour_seconds = hours * 3600
    mins = int((num_seconds - hour_seconds) / 60)
    min_seconds = mins * 60
    seconds = num_seconds - hour_seconds - min_seconds
    milliseconds = 0
    time = "".join((ensure_two_digits(hours),":",
                   ensure_two_digits(mins), ":",
                   ensure_two_digits(seconds), ":",
                   ensure_three_digits(milliseconds)))
    return time

def parse_hours(formatted_time):
    """takes a string of the form HH:MM:SS or HH:MM:SS:MMM 
    and returns the int HH"""
    return int(formatted_time[:2])

def parse_mins(formatted_time):
    """takes a string of the form HH:MM:SS or HH:MM:SS:MMM 
    and returns the int MM"""
    return int(formatted_time[3:5])

def parse_seconds(formatted_time):
    """takes a string of the form HH:MM:SS or HH:MM:SS:MMM 
    and returns the int SS"""
    return int(formatted_time[6:8])

def parse_milliseconds(formatted_time):
    """takes a string of the form HH:MM:SS:MMM and returns 
    the int MMM"""
    if len(formatted_time) > len('HH:MM:SS'):
        milliseconds = int(formatted_time[9:])
    else:
        milliseconds = 0
    return milliseconds

def format_time(hours, mins, seconds, milliseconds=None):
    """takes in a set of integers representing the time and 
    composes a string in the format HH:MM:SS, or if a 
    millisecond argument is supplied, returns a string 
    in the format HH:MM:SS.MMM."""
    time_values = time_values_in_range(hours, mins, seconds, milliseconds)
    hours, mins, seconds, milliseconds = time_values
    hours = str(ensure_two_digits(hours))
    mins = str(ensure_two_digits(mins))
    seconds = str(ensure_two_digits(seconds))
    formatted_time =  hours + ':' + mins + ':' + str(seconds)
    if milliseconds:
        milliseconds = str(ensure_three_digits(milliseconds))
    else: 
        milliseconds = str(ensure_three_digits(0))
    formatted_time = formatted_time + ':' + milliseconds
    return formatted_time

def time_values_in_range(hours, mins, seconds, milliseconds):
    """adjust time values to ensure that they all lie in 
    acceptable ranges."""
    if milliseconds:
        if milliseconds >= 1000:
            seconds = seconds + 1
            milliseconds = milliseconds - 1000
        if milliseconds < 0:
            seconds = seconds - 1
            milliseconds = milliseconds + 1000
    if seconds >= 60:
        mins = mins + 1
        seconds = seconds - 60
    if seconds < 0:
        mins = mins - 1
        seconds = seconds + 60
    if mins >= 60:
        hours = hours + 1
        mins = mins - 60
    if mins < 0:
        hours = hours - 1
        mins = mins + 60
    return (hours, mins, seconds, milliseconds)


def offset_time(time, offset):
    """takes a time in the format 'HH:MM:SS:mmm' and a millisecond
    offset between -999 and 999 and returns a formatted time 
    in the form `HH:MM:SS:mmm` where H = hours, M = minutes, 
    S = seconds, m = milliseconds"""
    hours = parse_hours(time)
    mins = parse_mins(time)
    seconds = parse_seconds(time)
    milliseconds = parse_milliseconds(time)
    initial_time =  format_time(hours, mins, seconds, milliseconds)
    formatted_time = add_milliseconds(initial_time, offset)
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

def add_milliseconds(time, milliseconds):
    """returns a formatted string in the form 
    HH:MM:SS:MMM in which the given number of milliseconds
    have been added (or subtracted if milliseconds is 
    negative) to the specified time."""
    hours = parse_hours(time)
    mins = parse_mins(time)
    seconds = parse_seconds(time)
    milliseconds = parse_milliseconds(time) + milliseconds
    time = format_time(hours, mins, seconds, milliseconds)
    return time

def get_times_in_interval(interval, step):
    """returns a list of times in the given interval 
    separated by the number of milliseconds specified
    by 'step'."""
    current_time = interval[0]
    times = [current_time]
    while current_time <= interval[1]:
        current_time = add_milliseconds(current_time, step)
        times.append(current_time)
    return times

def get_contiguous_intervals(times):
    """given a list of times separated by at least 
    a second, returns a list of pairs of the form 
    (start, stop) defining the (inclusive) ends of 
    a contiguous time interval in 'times'."""
    head = tail = time_to_seconds(times[0])
    intervals = []
    idx = 1
    while idx < len(times):   
        next_sec = time_to_seconds(times[idx])
        if next_sec - tail > 1:
            intervals.append((seconds_to_time(head), 
                              seconds_to_time(tail)))
            head = tail = next_sec
        else:
            tail = next_sec
        idx = idx + 1
    intervals.append((seconds_to_time(head), 
                      seconds_to_time(tail)))
    return intervals