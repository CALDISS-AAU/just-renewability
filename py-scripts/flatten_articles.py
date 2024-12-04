#!/usr/bin/env python
# coding: utf-8

import os
from os.path import join
import json
import pandas as pd
import re

# Script for flattening articles due to error in retrieve script (using append instead of concatenating lists)

# PATHS AND DIRS
project_dir = join('/work', 'CALDISS-projects', 'Leverancer', 'dlvr_just-renewability_F24')
data_dir = join(project_dir, 'data')

arg_data_p = join(data_dir, 'articles_arg_raw.json')
da_data_p = join(data_dir, 'articles_da_raw.json')
sp_data_p = join(data_dir, 'articles_sp_raw.json')

data_paths = [arg_data_p, da_data_p, sp_data_p]

# Function for flattening list (Code Copilot)
def flatten_list(mixed_list):
    """
    Flattens a mixed list containing dictionaries and lists of dictionaries
    into a single list of dictionaries.
    """
    flattened = []
    
    for item in mixed_list:
        if isinstance(item, dict):
            # If item is a dictionary, add to the flattened list
            flattened.append(item)
        elif isinstance(item, list):
            # If item is a list, extend the flattened list recursively
            flattened.extend(flatten_list(item))
        else:
            raise ValueError("Unsupported type found in list: {}".format(type(item)))
    
    return flattened

# Flatten articles
for data_p in data_paths:
    ## read
    with open(data_p, 'r') as f:
        data = json.load(f)
    
    ## flatten
    data['articles'] = flatten_list(data.get('articles'))

    ## dump
    with open(data_p, 'w') as f:
        json.dump(data, f)
