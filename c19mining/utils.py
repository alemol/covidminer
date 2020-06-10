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
from datetime import datetime

# all paths to data resources are relative to the project home
# this should be the only place to set paths.
HOME = str(Path(dirname(abspath(__file__))).parent)

# Medical Resources
COVID19_DATA = 'resources/covid19.csv'
COVID19_SYMPTOMS_DATA = 'resources/covid19_sintomas.csv'
COVID19_MORBIDITIES_DATA = 'resources/covid19_comorbilidades.csv'
COVID19_SAMPLING = 'resources/muestras.txt'
COVID19_DECEASE = 'resources/decesos.txt'
WIKI_SYMPTOMS_DATA = 'resources/sintomas_wikidata.csv'
CANONICAL_SYMPTOMS = 'resources/canonical_symptoms.csv'
CANONICAL_COMORBS = 'resources/canonical_comorbilidades.csv'
WIKI_DESEASES_DATA = 'resources/enfermedad_wikidata.csv'
COVID_DESEASE_DATA = 'resources/enf.csv'
DRUGS_DATA = 'resources/drogas.txt'

# Data
# UPLOADS DIRS
ADMISSIONS_DIRNAME = 'data/xmls/ingresos'
DISCHARGES_DIRNAME = 'data/xmls/egresos'
UPLOAD_DIRNAME = 'data/uploads'
# GENERATED DATA
EXTRACTIONS_DIRNAME = 'data/extracciones'
# OUTCOMES 
EXCELS_DIR = 'data/excels'
AMCHARTS_DIRNAME = 'data/amcharts'
# Unittest
TEST_TEXT = 'data/test/notamed.txt'
# BACK LOG SYSTEM
LOG_DIRNAME = 'log'

ALLOWED_EXTENSIONS = set(['xml','txt', 'pdf', 'jpg', 'jpeg'])

# These are the canonical names to concept

canonical_covid_name = {
    'Q84263196':   'covid-19',
    'Q2633267' :   'neumonía',
}

canonical_comorb_names = {
    'Q23900716':   'enfermedad ocupacional cardiovascular',
    'Q55789055':   'enfermedad cardiovascular rara',
    'Q18555060':   'aterosclerosis cardiovascular',
    'Q736715':   'insuficiencia renal crónica',
    'Q389735':   'enfermedad cardiovascular',
    'Q877827':   'cetoacidosis diabética',
    'Q631361':   'etinopatía diabética',
    'Q41861':   'hipertensión arterial',
    'Q126691':   'diabetes gestacional',
    'Q220551':   'diabetes insípida',
    'Q1455316':   'inmunosupresión',
    'Q826759':   'asma aguda severa',
    'Q2551913':   'asma ocupacional',
    'Q3025883':   'diabetes tipo 2',
    'Q124407':   'diabetes tipo 1',
    'Q52856':   'pie diabético',
    'Q663041':   'diabetes mody',
    'Q939364':   'cardiopatías',
    'Q662860':   'tabaquismo',
    'Q332428':   'sobrepeso',
    'Q12206':   'diabetes',
    'Q12174':   'obesidad',
    'Q12199':   'vih/sida',
    'Q199804':   'epoc',
    'Q35869':   'asma',
    'Q15787':   'vih'
}

def get_time():
    """creates datestamp """
    now = datetime.now()
    #datestamp = now.strftime("%d_%m_%Y_%Hh%M")
    datestamp = now.strftime("%d_%m_%Y")
    return datestamp

def admissions_dir():
    path = join(HOME, ADMISSIONS_DIRNAME)
    return path

def discharges_dir():
    path = join(HOME, DISCHARGES_DIRNAME)
    return path

def extractions_dir():
    path = join(HOME, EXTRACTIONS_DIRNAME)
    return path

def amcharts_dir():
    path = join(HOME, AMCHARTS_DIRNAME)
    return path

def excels_dir():
    path = join(HOME, EXCELS_DIR)
    return path

def uploads_dir():
    path = join(HOME, UPLOAD_DIRNAME)
    return path

def canonical_symptoms_order():
    csymptoms_path = join(HOME, CANONICAL_SYMPTOMS)
    with open(csymptoms_path, 'r') as f:
        canonical_order = [l.split('\t')[0] for l in f.readlines()]
    return canonical_order

def canonical_symptoms_name():
    csymptoms_path = join(HOME, CANONICAL_SYMPTOMS)
    with open(csymptoms_path, 'r') as f:
        canonical_names = {l.split('\t')[0]: (l.split('\t')[1]).strip('\n') for l in f.readlines()}
    return canonical_names

def canonical_comorbs_order():
    resource_path = join(HOME, CANONICAL_COMORBS)
    with open(resource_path, 'r') as f:
        canonical_order = [l.split('\t')[0] for l in f.readlines()]
    return canonical_order

def canonical_comorbs_name():
    resource_path = join(HOME, CANONICAL_COMORBS)
    with open(resource_path, 'r') as f:
        canonical_names = {l.split('\t')[0]: (l.split('\t')[1]).strip('\n') for l in f.readlines()}
    return canonical_names

def covid19():
    symptoms_path = join(HOME, COVID19_DATA)
    return load_csv(symptoms_path)

def covid_regex():
    data_path = join(HOME, COVID19_DATA)
    regex = csv2regex(data_path)
    return regex

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

def drugs_regex():
    symptoms_path = join(HOME, DRUGS_DATA)
    regex = csv2regex(symptoms_path)
    return regex

def context_covid_regex():
    data_path = join(HOME, COVID19_DATA)
    regex = csv2contextregex(data_path)
    return regex

def covid_namedict():
    data_path = join(HOME, COVID19_DATA)
    namedict = load_names_dict(data_path)
    return namedict

def context_symptoms_regex():
    data_path = join(HOME, WIKI_SYMPTOMS_DATA)
    regex = csv2contextregex(data_path)
    return regex

def symptoms_namedict():
    data_path = join(HOME, WIKI_SYMPTOMS_DATA)
    namedict = load_names_dict(data_path)
    return namedict

def context_morbidities_regex():
    data_path = join(HOME, COVID19_MORBIDITIES_DATA)
    regex = csv2contextregex(data_path)
    return regex

def morbidities_namedict():
    data_path = join(HOME, COVID19_MORBIDITIES_DATA)
    namedict = load_names_dict(data_path)
    return namedict

def context_deseases_regex():
    data_path = join(HOME, WIKI_DESEASES_DATA)
    regex = csv2contextregex(data_path)
    return regex

def deseases_namedict():
    data_path = join(HOME, WIKI_DESEASES_DATA)
    namedict = load_names_dict(data_path)
    return namedict

def covid19_comorbidities():
    comorbidities_path = join(HOME, COVID19_MORBIDITIES_DATA)
    return load_csv(comorbidities_path)

def covid19_sampling():
    data_path = join(HOME, COVID19_SAMPLING)
    return load_txt(data_path)

def covid19_decease():
    data_path = join(HOME, COVID19_DECEASE)
    return load_txt(data_path)

def decease_regex():
    data_path = join(HOME, COVID19_DECEASE)
    regex = list2contextregex(data_path)
    return regex

def sampling_regex():
    data_path = join(HOME, COVID19_SAMPLING)
    regex = list2contextregex(data_path)
    return regex

def load_txt(filepath):
    with open(filepath) as f:
        lines = [l.replace('\n', '') for l in f.readlines()]
    return lines

def load_csv(filepath):
    df = pd.read_csv(filepath, sep='\t')
    return list(zip(df.id, df.name))

def load_names_dict(filepath):
    df = pd.read_csv(filepath, sep='\t')
    d = dict({name:code for name, code in list(zip(df.name, df.id))})
    return d

def mkdir(out, name):
    create_dir = join(out, name)
    if not exists(create_dir):
        os.makedirs(create_dir)
    return create_dir

def list2contextregex(path, context_size=6):
    with open(path) as f:
        joined = '|'.join([l.strip('\n') for l in f.readlines()])
    regex = r'((\w+\W+){0,5}('+joined+r')(\W+\w+){0,5})'
    compiled = re.compile(regex)
    return compiled

def csv2regex(path):
    tuple_list = load_csv(path)
    regex = r'(?P<matched>'+('|'.join([r'\b'+name+r'\b' for (_, name) in tuple_list]))+')'
    compiled = re.compile(regex)
    return compiled

def csv2contextregex(path, context_size=6):
    tuple_list = load_csv(path)
    joined = '|'.join([r'\b'+name+r'\b' for (_, name) in tuple_list])
    regex = r'((\w+\W+){0,5}('+joined+r')(\W+\w+){0,5})'
    compiled = re.compile(regex)
    return compiled

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_xml_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['xml','XML']

def log_file():
    log_path = join(HOME, LOG_DIRNAME, 'error.log')
    return log_path
