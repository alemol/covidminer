# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

from tmining.utils import covid19, covid19_symptoms, covid19_sampling, covid19_comorbidities
import re
import simplejson as json


class MedNotesMiner(object):
    """Medical notes data miner for Covid-19 insights"""
    def __init__(self, text_utf8, covid19_db=None, symptoms_db=None, sampling_db=None, morbidities_db=None):
        super(MedNotesMiner, self).__init__()
        self.text = text_utf8
        self.clues = {'texto': self.text}
        self.lower_text = self.text.lower()
        if not covid19_db:
            self.covid19_db = covid19()
        if not symptoms_db:
            self.symptoms_db = covid19_symptoms()
        if not sampling_db:
            self.sampling_db = covid19_sampling()
        if not morbidities_db:
            self.morbidities_db = covid19_comorbidities()

    def check_covid19(self, lower_case=True):
        """match covid-19 mentions"""
        self.clues['COVID-19'] = {}

        # seek for covid matches
        for (covid_key, covid_name) in self.covid19_db:
            #TODO: method argumen contex_size
            regex = r'((\w+\W+){0,5}\b'+covid_name+r'\b(\W+\w+){0,5})'
            for covid_mention in re.finditer(regex, self.lower_text):
                context_mention = '...'+(covid_mention.groups()[0]).replace('\n', ' ')+'...'
                covid_info = {'mención':context_mention,
                              'wikidata': 'https://www.wikidata.org/wiki/{}'.format(covid_key)}

                if not covid_name in self.clues['COVID-19']:
                    self.clues['COVID-19'][covid_name] = [covid_info]
                    continue

                self.clues['COVID-19'][covid_name].append(covid_info)

    def check_symptoms(self, lower_case=True):
        """match covid-19 symptoms"""
        self.clues['síntomas'] = {}

        # seek for symptoms matches
        for (sympt_key, sympt_name) in self.symptoms_db:
            #TODO: method argumen contex_size
            regex = r'((\w+\W+){0,5}\b'+sympt_name+r'\b(\W+\w+){0,5})'
            for sympt_mention in re.finditer(regex, self.lower_text):
                context_mention = '...'+(sympt_mention.groups()[0]).replace('\n', ' ')+'...'
                # TODO: filter wikidata info selected
                # wikidict = get_entity_dict_from_api(sympt_key)
                # external_info = wikidict['claims'] if 'claims' in wikidict else ''
                sympt_info = {'mención':context_mention,
                              'wikidata': 'https://www.wikidata.org/wiki/{}'.format(sympt_key)}

                if not sympt_name in self.clues['síntomas']:
                    self.clues['síntomas'][sympt_name] = [sympt_info]
                    continue

                self.clues['síntomas'][sympt_name].append(sympt_info)

    def check_comorbidities(self, lower_case=True):
        """match covid-19 comorbidities"""
        self.clues['comorbilidad'] = {}

        # seek for comorbidities matches
        for (comorbidity_key, comorbidity_name) in self.morbidities_db:
            #TODO: method argumen contex_size
            regex = r'((\w+\W+){0,5}\b'+comorbidity_name+r'\b(\W+\w+){0,5})'
            for morbid_mention in re.finditer(regex, self.lower_text):
                context_mention = '...'+(morbid_mention.groups()[0]).replace('\n', ' ')+'...'
                # TODO: filter wikidata info selected
                # wikidict = get_entity_dict_from_api(comorbidity_key)
                # external_info = wikidict['claims'] if 'claims' in wikidict else ''
                comorbidity_info = {'mención':context_mention,
                              'wikidata': 'https://www.wikidata.org/wiki/{}'.format(comorbidity_key)}

                if not comorbidity_name in self.clues['comorbilidad']:
                    self.clues['comorbilidad'][comorbidity_name] = [comorbidity_info]
                    continue

                self.clues['comorbilidad'][comorbidity_name].append(comorbidity_info)

    def check_sampling(self):
        """match covid-19 sampling mentions"""
        self.clues['muestreos'] = []

        # seek for sampling matches
        for sampling_cueword in self.sampling_db:
            regex = r'((\w+\W+){0,5}\b'+sampling_cueword+r'\b(\W+\w+){0,5})'
            for samp_mention in re.finditer(regex, self.lower_text):
                context_mention = '...'+(samp_mention.groups()[0]).replace('\n', ' ')+'...'
                self.clues['muestreos'].append({'mención': context_mention})

