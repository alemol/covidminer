# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".", ".."))

from c19mining.textprocessing import Tokenizer
from c19mining.utils import (HOME, explore_dir,
                             sampling_regex, decease_regex,
                             covid19, covid_namedict,
                             context_morbidities_regex, morbidities_namedict,
                             context_symptoms_regex, symptoms_namedict,
                             context_deseases_regex, deseases_namedict,
                             context_drugs_regex, drugs_namedict)
import re
import pandas as pd
import simplejson as json


class MedNotesMiner(object):
    """Medical notes data miner for Covid-19 insights"""
    def __init__(self, text_utf8, init_data=None):
        super(MedNotesMiner, self).__init__()
        self.wikidata_url = 'https://www.wikidata.org/wiki/'
        self.text = text_utf8
        self.clues = init_data if init_data else dict()
        self.clues['texto'] = self.text
        self.working_text = self.preproc_tex()
        self.sampling_re = sampling_regex()
        self.decease_re = decease_regex()
        self.covid19_db = covid19()
        self.covid_dict = covid_namedict()
        self.symptoms_re = context_symptoms_regex()
        self.symptoms_dict = symptoms_namedict()
        self.drugs_re = context_drugs_regex()
        self.drugs_dict = drugs_namedict()
        self.morbidities_re = context_morbidities_regex()
        self.morbidities_dict = morbidities_namedict()

    def preproc_tex(self):
        tokenizer = Tokenizer()
        lower_text = self.text.lower()
        tokenized = tokenizer.split_tokens(lower_text)
        return tokenized

    def check_covid19(self, lower_case=True):
        """match covid-19 mentions"""
        patch_pattern = r'(hospital receptor de covid|receptora de covid|hospital de concentracion para covid)'
        self.clues['COVID-19'] = {}

        # seek for covid matches
        for (covid_key, covid_name) in self.covid19_db:
            #TODO: method argumen contex_size
            regex = r'((\w+\W+){0,5}\b'+covid_name+r'\b(\W+\w+){0,5})'
            for covid_mention in re.finditer(regex, self.working_text):
                context_mention = '...'+(covid_mention.groups()[0]).replace('\n', ' ')+'...'
                covid_info = {'descripción': covid_name,
                              'mención': context_mention,
                              'wikidata': '{}{}'.format(self.wikidata_url, covid_key)}

                if re.search(patch_pattern, context_mention, flags=0):
                    #print('Negación de "{}"" detectada:\n\n{}\n'.format(covid_name, context_mention))
                    continue

                if not covid_key in self.clues['COVID-19']:
                    self.clues['COVID-19'][covid_key] = [covid_info]
                else:
                    self.clues['COVID-19'][covid_key].append(covid_info)

    def check_symptoms(self, lower_case=True):
        """match covid-19 symptoms"""
        self.clues['síntomas'] = {}

        # seek for symptoms matches
        for symptom_mention in self.symptoms_re.finditer(self.working_text):
            context_mention = '...'+(symptom_mention.groups()[0]).replace('\n', ' ')+'...'
            symptom_name = symptom_mention.groups()[2]
            symptom_key = self.symptoms_dict[symptom_name]
            symptom_info = {'descripción': symptom_mention.groups()[2],
                            'mención': context_mention,
                            'wikidata': '{}{}'.format(self.wikidata_url, symptom_key)}

            patch_pattern = r'(sin '+symptom_name+r'|niega '+symptom_name+r'|sin compañía de '+symptom_name+r'|ni '+symptom_name+r')'
            if re.search(patch_pattern, context_mention, flags=0):
                #print('Negación de "{}"" detectada:\n\n{}\n'.format(symptom_name, context_mention))
                continue

            if not symptom_key in self.clues['síntomas']:
                self.clues['síntomas'][symptom_key] = [symptom_info]
            else:
                self.clues['síntomas'][symptom_key].append(symptom_info)

    def check_drugs(self, lower_case=True):
        """match covid-19 symptoms"""
        self.clues['medicamentos'] = {}

        # seek for matches
        for drugs_mention in self.drugs_re.finditer(self.working_text):
            context_mention = '...'+(drugs_mention.groups()[0]).replace('\n', ' ')+'...'
            drug_name = drugs_mention.groups()[2]
            drug_key = self.drugs_dict[drug_name]
            drug_info = {'descripción': drugs_mention.groups()[2],
                            'mención': context_mention,
                            'SAICA': '{}'.format(drug_key)}

            if not drug_key in self.clues['medicamentos']:
                self.clues['medicamentos'][drug_key] = [drug_info]
            else:
                self.clues['medicamentos'][drug_key].append(drug_info)

    def check_comorbidities(self, lower_case=True):
        """match covid-19 comorbidities"""
        self.clues['comorbilidades'] = {}

        # seek for comorbidities matches
        for morbid_mention in self.morbidities_re.finditer(self.working_text):
            context_mention = '...'+(morbid_mention.groups()[0]).replace('\n', ' ')+'...'
            morbid_name = morbid_mention.groups()[2]
            comorbidity_key = self.morbidities_dict[morbid_name]
            comorbidity_info = {'descripción': morbid_mention.groups()[2],
                                'mención': context_mention,
                                'wikidata': '{}{}'.format(self.wikidata_url, comorbidity_key)}

            patch_pattern = r'(sin '+morbid_name+r'|niega '+morbid_name+r'|sin compañía de '+morbid_name+r'|ni '+morbid_name+r'|'+morbid_name+'nega'+r')'
            if re.search(patch_pattern, context_mention, flags=0):
                #print('Negación de "{}"" detectada:\n\n{}\n'.format(morbid_name, context_mention))
                continue

            if not comorbidity_key in self.clues['comorbilidades']:
                self.clues['comorbilidades'][comorbidity_key] = [comorbidity_info]
            else:
                self.clues['comorbilidades'][comorbidity_key].append(comorbidity_info)

    def check_sampling(self):
        """match covid-19 sampling mentions"""
        self.clues['muestreos'] = []

        # seek for sampling matches
        for sampling_mention in self.sampling_re.finditer(self.working_text):
            context_mention = '...'+(sampling_mention.groups()[0]).replace('\n', ' ')+'...'
            self.clues['muestreos'].append({'mención': context_mention})

    def check_decease(self):
        """match decease mentions"""
        self.clues['defunciones'] = []

        # seek for decease matches
        for decease_mention in self.decease_re.finditer(self.working_text):
            context_mention = '...'+(decease_mention.groups()[0]).replace('\n', ' ')+'...'
            self.clues['defunciones'].append({'mención': context_mention})


if __name__ == '__main__':
    texto_urgencia ='''
    Paciente con presencia d epolipnea, orientado en tiempo, lugar y espacio. Funciones mentales superiores conservadas. Tegumentos
    deshidratados. Craneo: Sin palpar endostosis ni exostosis y sin detectar crepitaciones. Pupilas Isocéricas y normorrefléxicas, escleréticas sin
    hiperemia, Narinas permeables, mucosas orales deshidratadas. Cuello integro, corto, cilindrico y sin adenomegalias cervicales, sin datos de
    ingurgitacién yugular. Térax integro, con polipnea aumento de la transmisién vocal hipoventilacién de lado izquierdo basal con presencia de
    estertores finos de predominio de lado derecho, sin integrar ningun sindrome pleuropulmonar. Area cardiaca con ruidos ritmicos y sincrénicos
    pero con aumento de tono e intensidad, Abdomen globoso a expensas de paniculo adiposo, normoperistalsis, sin palpar visceromegalias ni
    despertar puntos dolorosos a la palpacién profunda, timpanismo en todo marco colénico. Extremidades tordcicas integras y sin alteraciones en
    sus arcos de movilidad, llenado capilar 2 segundos. Extremidades inferiores: sin edema, con pulsos periféricos presentes y sincrénicos, con
    llenado capilar 4 segundos.
    EN ESPERA DE RECABAR MUESTRAS PARA PANEL VIRAL Y COVID 19.
    '''
    # Information Extraction
    covid_seeker = MedNotesMiner(texto_urgencia)
    covid_seeker.check_covid19()
    covid_seeker.check_symptoms()
    covid_seeker.check_sampling()
    covid_seeker.check_decease()
    covid_seeker.check_comorbidities()

    covid_insights =  json.dumps(covid_seeker.clues, ensure_ascii=False, encoding='utf-8', indent=2)
    print(covid_insights)
