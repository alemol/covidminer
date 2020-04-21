# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

import os
import re
from os.path import (join, exists)
from shutil import rmtree
import pandas as pd 


def load_txt(filepath):
    with open(filepath) as f:
        lines = [l.replace('\n', '') for l in f.readlines()]
    return lines

def load_csv(filepath):
    df = pd.read_csv(filepath, sep='\t')
    return list(zip(df.id, df.name))

def mkdir(out, name):
    create_dir = join(out, name)
    if not exists(create_dir):
        os.makedirs(create_dir)
    return create_dir

def explore_dir(explore_dir, yield_extension='txt'):
    for root, directory, files in os.walk(explore_dir, topdown=True):
            for file in sorted(files, key=natural_keys):
                if file.endswith(yield_extension):
                    full_path = join(root, file)
                    yield(full_path, file)

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
