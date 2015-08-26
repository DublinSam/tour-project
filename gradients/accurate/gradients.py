from __future__ import division

import numpy as np
from xml.dom import minidom

def build_path(stage_id):
    """constructs the path to the .tcx file for the
    given stage."""
    PATH = """/Users/samuelalbanie/aims_course/project_two/code/tour_data/strava_profiles/raw/"""
    return PATH + "Stage" + str(stage_id) + ".tcx"

def get_xml_values(stage_id, target):
    """returns the values contained in the dom nodes 
    representing the xml data for the given stage_id.
    `target` is used to select the data of interest."""
    path = build_path(stage_id)
    dom = minidom.parse(path)
    data_keys = {'elevations': 5, 'distances': 7}
    data_id = data_keys[target]
    values = []
    for node in dom.getElementsByTagName('Trackpoint'):
        values.append(node.childNodes[data_id].firstChild.nodeValue)
    return values

def get_elevations(stage_id):
    """returns a list of elevations for the given stage."""
    elevations = get_xml_values(stage_id, "elevations")
    elevations = [float(elevation) for elevation in elevations]
    return elevations

def get_precise_distances(stage_id):
    """returns a list of 'precise' distances, measured 
    in metres.  This is necessary for the purposes of 
    producing accurate gradients. After this has been done, 
    the distances are converted to `km` for general use."""
    precise_distances = get_xml_values(stage_id, "distances")
    precise_distances = [round(float(distance), 1) for distance in precise_distances]
    return precise_distances

def calculate_gradients(elevations, distances):
    """returns a list of gradients. These are calculated so 
    that the gradient at marker n is estimated using the altitudes
    of markers n-1 and n. The gradient for the first 
    segment i always set to zero."""
    gradients = [0]
    for idx, elevation in enumerate(elevations):
        if idx > 0:
            distance = distances[idx] - distances[idx - 1]
            gradient = (elevations[idx] - elevations[idx - 1]) / distance
            gradients.append(gradient)
    # convert gradients to percentages
    gradients = [round(gradient * 100,1) for gradient in gradients] 
    return gradients

def find_gradient_at_distance(target_distance, distances, gradients):
    """finds the gradient at the marker located closest to 
    the given target_distance.""" 
    closest_marker = min(distances, key=lambda x:abs(x - target_distance))
    target_idx = distances.index(closest_marker)
    return gradients[target_idx]

def find_gradient(stage_id, distance_to_go):
    """calculates the gradient of the given stage with 
    `distance_to_go` km remaining."""
    elevations = get_elevations(stage_id)    
    distances = get_precise_distances(stage_id)
    gradients = calculate_gradients(elevations, distances)

    # convert from metres to km
    distances = [round(distance / 1000, 2) for distance in distances]
    target_distance = max(distances) - distance_to_go
    target_gradient = find_gradient_at_distance(target_distance, distances, gradients)
    return target_gradient