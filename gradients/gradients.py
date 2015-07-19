import csv
import numpy as np
from scipy.misc import imread

PATH = '/Users/samuelalbanie/aims_course/project_two/code/tour_data/stage_profile_silhouettes/'

def all_stages():
    with open (PATH + 'stage_data.csv') as csvfile:
        stage_reader = csv.reader(csvfile, delimiter=',')
        stages = list(stage_reader)
    return stages

def all_climbs():
    with open (PATH + 'climb_data.csv') as csvfile:
        climb_reader = csv.reader(csvfile, delimiter=',')
        climbs = list(climb_reader)
    return climbs

class Stage:

    def __init__(self, stage_num):
        self.stage_num = stage_num
        self.calib_factor = 1 # initialize to this value
        self.build_map(stage_num)
        self.build_trace()
        self.find_stage_dims(stage_num)
        self.set_calibration_factor()

    def build_map(self, stage_num):
        stage = imread(PATH + 'traces/stage-' + str(stage_num) + '-trace.png')
        self.map = stage[:,:,3].T

    def find_stage_dims(self, stage_num):
        stages = all_stages()
        dimensions = {}
        dimensions['stage'] = stage_num
        dimensions['length'] = int(float(stages[stage_num][1]) * 1000) # given in metres
        dimensions['altitude range'] = int(stages[stage_num][4])
        dimensions['min altitude'] = int(stages[stage_num][2])
        dimensions['max altitude'] = int(stages[stage_num][3])
        self.stage_dims = dimensions

    def build_trace(self):
        """returns a trace line a single pixel thick"""
        for i in range(0, self.map.shape[0]):
            first_max = True
            for j in range(0, self.map.shape[1]):
                col_max = np.amax(self.map[i,:])
                if self.map[i,j] == col_max and first_max:
                    if col_max > 0:
                        self.map[i,j] = 1
                        first_max = False
                else:
                    self.map[i,j] = 0
        self.trace = self.map.T
        self.find_trace_dimensions()

    def get_non_zero_cols(self, trace):
        indices = []
        counter = 0
        for col in trace.T:
            non_zero = np.nonzero(col)[0]
            if not np.array_equal(non_zero, np.array([])):
                indices.append(counter)
            counter += 1
        return indices

    def find_trace_dimensions(self):
        col_indices = self.get_non_zero_cols(self.trace)
        row_indices = self.get_non_zero_cols(self.trace.T)
        self.trace_dims = {
                'min_x': min(col_indices), 
                'max_x': max(col_indices), 
                'min_y': min(row_indices), 
                'max_y': max(row_indices)}

    def relative_altitude(self, pixel_x):
        absolute_position = np.where(self.trace[:,pixel_x] == 1)[0][0]
        altitude_range = self.trace_dims['max_y'] - self.trace_dims['min_y']
        relative_altitude = (self.trace_dims['max_y'] - absolute_position) / altitude_range
        return relative_altitude

    def altitude(self, pixel_x):
        altitude_range = self.stage_dims['altitude range']
        altitude_gain = self.relative_altitude(pixel_x) * altitude_range
        altitude = self.stage_dims['min altitude'] + altitude_gain
        return altitude

    def km_to_pixel(self, km):
        progress = (km * 1000) / self.stage_dims['length']
        pixel_range = self.trace_dims['max_x'] - self.trace_dims['min_x']
        pixel = self.trace_dims['min_x'] + (progress * pixel_range)
        return round(pixel)

    def slope_to_degrees(self, slope):
        return np.degrees(np.arctan(slope))

    def gradient(self, km, grad_distance):
        current_pixel = self.km_to_pixel(km)
        anchor_pixel = self.km_to_pixel(km - grad_distance)
        current_altitude = self.altitude(current_pixel)
        anchor_altitude = self.altitude(anchor_pixel)
        grad = (current_altitude - anchor_altitude) / (grad_distance * 1000)
        uncalibrated = self.slope_to_degrees(grad)
        return (uncalibrated / self.calib_factor)

    def get_climbs(self):
        climb_data = all_climbs()
        climbs = []
        for row in climb_data[1:]:
            if int(row[0]) == self.stage_num:
                climb = {}
                climb['name'] = row[1]
                climb['location'] = float(row[2])
                climb['length'] = float(row[3])
                climb['degrees'] = float(row[4])
                climb['category'] = row[5]
                climbs.append(climb)
        self.climbs = climbs

    def set_calibration_factor(self):
        calibrations = []
        self.get_climbs()
        for climb in self.climbs:
            grad = self.gradient(climb['location'], climb['length'])
            true_grad = climb['degrees']
            calibrations.append(grad / true_grad)
        calib_factor = np.mean(calibrations)
        self.calib_factor = calib_factor