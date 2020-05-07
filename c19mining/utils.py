# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

import os
import re
from os.path import (join, exists, dirname, abspath)
from pathlib import Path
from shutil import rmtree
import pandas as pd 

# all paths to data resources are relative to the project home
# this should be the only place to set them.
HOME = str(Path(dirname(abspath(__file__))).parent)
COVID19_DATA = 'resources/covid19.csv'
COVID19_SYMPTOMS_DATA = 'resources/covid19_sintomas.csv'
COVID19_COMORBIDITIES_DATA = 'resources/covid19_comorbilidades.csv'
COVID19_SAMPLING = 'resources/muestras.txt'
WIKI_SYMPTOMS_DATA = 'resources/sintomas_wikidata.csv'
WIKI_DESEASES_DATA = 'resources/enfermedad_wikidata.csv'
COVID_DESEASE_DATA = 'resources/enf.csv'
PLOTS_DIR = 'plots'
UPLOAD_DIRNAME = 'uploads'
LOG_DIRNAME = 'log'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg'])

# These are the symptoms to report and their canonical names
canonical_symptoms_name = {
    'Q38933':   'fiebre',
    'Q35805':   'tos',
    'Q767485':  'fallo_respiratorio',
    'Q344873':  'sdra',
    'Q188008':  'disnea',
    'Q86':      'cefalea',
    'Q9690':    'cansancio',
    'Q40878':   'diarrea',
    'Q114085':  'congestión_nasal',
    'Q474959':  'mialgia',
    'Q647099':  'hemoptisis',
    'Q485831':  'linfopenia',
    'Q5445':    'anemia',
    'Q1076369': 'tormenta_de_citocinas',
    'Q3508755': 'síndrome_gripal'
}

canonical_symptoms_order = ['Q38933','Q35805', 'Q767485','Q344873', 'Q188008', 'Q86','Q9690','Q40878','Q114085','Q474959','Q647099','Q485831','Q5445','Q1076369','Q3508755']

def covid19():
    symptoms_path = join(HOME, COVID19_DATA)
    return load_csv(symptoms_path)

def covid19_symptoms():
    symptoms_path = join(HOME, COVID19_SYMPTOMS_DATA)
    return load_csv(symptoms_path)

def wiki_symptoms():
    symptoms_path = join(HOME, WIKI_SYMPTOMS_DATA)
    return load_csv(symptoms_path)

def wiki_deseases():
    symptoms_path = join(HOME, WIKI_DESEASES_DATA)
    return load_csv(symptoms_path)

def covid19_symptoms_regex():
    symptoms_path = join(HOME, COVID19_SYMPTOMS_DATA)
    regex = csv2regex(symptoms_path)
    return regex

def wiki_symptoms_regex():
    symptoms_path = join(HOME, WIKI_SYMPTOMS_DATA)
    regex = csv2regex(symptoms_path)
    return regex

def covid_deseases_regex():
    data_path = join(HOME, COVID_DESEASE_DATA)
    regex = csv2regex(data_path)
    return regex

def wiki_deseases_regex():
    data_path = join(HOME, WIKI_DESEASES_DATA)
    regex = csv2regex(data_path)
    return regex

def covid19_comorbidities():
    comorbidities_path = join(HOME, COVID19_COMORBIDITIES_DATA)
    return load_csv(comorbidities_path)

def covid19_sampling():
    sampling_path = join(HOME, COVID19_SAMPLING)
    return load_txt(sampling_path)

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

def csv2regex(path):
    tuple_list = load_csv(path)    
    regex =r'(?P<matched>'+('|'.join([r'\b'+name+r'\b' for (_, name) in tuple_list]))+')'
    return re.compile(regex)

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

def uploads_dir():
    uploads_path = join(HOME, UPLOAD_DIRNAME)
    return uploads_path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_file():
    log_path = join(HOME, LOG_DIRNAME, 'error.log')
    return log_path
