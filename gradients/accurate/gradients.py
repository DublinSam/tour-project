from __future__ import division

import numpy as np
from file_utils import get_paths
from xml.dom import minidom

MEASUREMENT_OFFSET = 0
ELEVATION_WINDOW_LENGTH = 25
GRADIENT_WINDOW_LENGTH = 3


def smooth(x, N):
    """takes an integer N (MUST BE ODD) as the order
    of a convolution filter to smooth x"""
    buffer_avg = np.zeros(int(N / 2))
    # extend x to handle convolution "off the ends"
    x_complete = np.hstack((buffer_avg, x, buffer_avg))
    smoothed_x = np.convolve(x_complete, np.ones((N,))/N, mode='valid')
    return smoothed_x

def get_xml_values(paths, target):
    """returns the values contained in the dom nodes 
    representing the xml data for the given stage_id.
    `target` is used to select the data of interest."""
    dom = minidom.parse(paths['strava'])
    data_keys = {'elevations': 5, 'distances': 7}
    data_id = data_keys[target]
    values = []
    for node in dom.getElementsByTagName('Trackpoint'):
        values.append(node.childNodes[data_id].firstChild.nodeValue)
    return values

def get_elevations(paths):
    """returns a list of smoothed elevations for the given stage."""
    elevations = get_xml_values(paths, "elevations")
    elevations = [float(elevation) for elevation in elevations]
    smooth_elevations = smooth(np.array(elevations), N=ELEVATION_WINDOW_LENGTH)
    return smooth_elevations

def get_precise_distances(paths):
    """returns a list of 'precise' distances, measured 
    in metres.  This is necessary for the purposes of 
    producing accurate gradients. After this has been done, 
    the distances are converted to `km` for general use."""
    precise_distances = get_xml_values(paths, "distances")
    precise_distances = [round(float(distance), 1) for distance in precise_distances]
    return precise_distances

def calculate_gradients(elevations, distances):
    """returns a list of gradients. These are calculated so 
    that the gradient at marker n is estimated using the altitudes
    of markers n - 6 and n + 6. The gradient for the first eight segments
    are set to zero."""
    gradients = 8 * [0]
    for idx, elevation in enumerate(elevations):
        if idx > 7 and idx < len(elevations) - 9:
            distance = distances[idx + 8] - distances[idx - 8]
            gradient = (elevations[idx + 8] - elevations[idx - 8]) / distance
            gradients.append(gradient)
    gradients.extend(8 * [0])
    # convert gradients to percentages
    gradients = [round(gradient * 100,1) for gradient in gradients] 
    smooth_gradients = smooth(np.array(gradients), N = GRADIENT_WINDOW_LENGTH)
    return smooth_gradients

def find_gradient_at_distance(target_distance, distances, gradients):
    """finds the gradient at the marker located closest to 
    the given target_distance.""" 
    closest_marker = min(distances, key=lambda x:abs(x - target_distance)) 
    closest_idx = distances.index(closest_marker)
    if closest_idx > MEASUREMENT_OFFSET:
        closest_idx = closest_idx - MEASUREMENT_OFFSET
	# prevent indexing errors
	closest_idx = min(closest_idx, len(gradients) - 1) 
    return gradients[closest_idx]

def find_gradient(paths, distance_to_go):
    """calculates the gradient of the given stage with 
    `distance_to_go` km remaining."""
    elevations = get_elevations(paths)    
    distances = get_precise_distances(paths)
    gradients = calculate_gradients(elevations, distances)

    # convert from metres to km
    distances = [round(distance / 1000, 2) for distance in distances]
    target_distance = max(distances) - distance_to_go
    target_gradient = find_gradient_at_distance(target_distance, distances, gradients)
    rounded_target = round(target_gradient, 1) 
    return rounded_target 
