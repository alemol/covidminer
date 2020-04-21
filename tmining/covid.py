# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

from tmining.utils import load_csv, load_txt
import re
import simplejson as json


class MedNotesMiner(object):
    """Medical notes data miner for Covid-19 insights"""
    def __init__(self, text_utf8, symptoms_db, sampling_db):
        super(MedNotesMiner, self).__init__()
        self.text = text_utf8
        self.clues = {'texto': self.text}
        self.lower_text = self.text.lower()
        self.symptoms_db = load_csv(symptoms_db)
        self.sampling_db = load_txt(sampling_db)        

    def check_symptoms(self, lower_case=True):
        """match covid-19 symptoms"""
        self.clues['síntomas'] = {}

        # seek for symptoms matches
        for (sympt_key, sympt_name) in self.symptoms_db:
            #TODO: method argumen contex_size
            regex = r'((\w+\W+){0,4}\b'+sympt_name+r'\b(\W+\w+){0,4})'
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

    def check_sampling(self):
        """match covid-19 sampling mentions"""
        self.clues['muestreos'] = []

        # seek for sampling matches
        for sampling_cueword in self.sampling_db:
            regex = r'((\w+\W+){0,4}\b'+sampling_cueword+r'\b(\W+\w+){0,4})'
            for samp_mention in re.finditer(regex, self.lower_text):
                context_mention = '...'+(samp_mention.groups()[0]).replace('\n', ' ')+'...'
                self.clues['muestreos'].append({'mención': context_mention})

