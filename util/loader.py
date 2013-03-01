#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 08, 2012
Copyright 2012, All rights reserved
'''

import copy
import math
import os
import yaml

from array import array

def load_file(filename):
    '''
    Load yaml data from file
    
    raise RuntimeError in case of error: file does not exist or load failed
    '''

    if not os.path.exists(filename):
        raise RuntimeError("input file does not exist: " + filename)

    data = None
    with open(filename) as input_:
        data = yaml.load('\n'.join(input_.readlines()))

    if not data:
        raise RuntimeError("failed to read input data from " + filename)

    return data

def load_data(filename, scale):
    '''
    Load several YAML files and put into Data object

    The Data attributes are defined by argument names, e.g.:

        data = load_data(low="low_file.yaml", high="high_file.yaml")
        print(data.low)
        print(data.high)
    '''
    data = load_file(filename)
    if scale != 1.0:
        for key in data:
            data[key] = [scale*x for x in data[key]]

    return data

def get_limits(data):
    '''Convert yaml data into Dictionary like format'''
    limits = {
            "x": array('d'),
            "xerr": array('d'),
            "expected": array('d'),
            "observed": array('d'),
            "observed_x": array('d'),
            "one_sigma_down": array('d'),
            "one_sigma_up": array('d'),
            "two_sigma_down": array('d'),
            "two_sigma_up": array('d')
            }

    def fill(data, mass, to_, x=None):
        v = data[mass]
        to_["x"].append(x if x else mass)
        to_["xerr"].append(0)
        to_["expected"].append(v[0])
        to_["one_sigma_up"].append(v[1])
        to_["one_sigma_down"].append(math.fabs(v[2]))
        to_["two_sigma_up"].append(v[3])
        to_["two_sigma_down"].append(math.fabs(v[4]))
        to_["observed"].append(v[5])
        to_["observed_x"].append(x if x else mass)

    for k in sorted(data):
        fill(data, k, limits)

    return limits 
