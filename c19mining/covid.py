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
                             covid19, covid19_symptoms,
                             wiki_symptoms, wiki_deseases,
                             covid19_sampling, covid19_comorbidities,
                             wiki_deseases_regex, wiki_symptoms_regex,
                             context_covid_regex, covid_namedict,
                             context_morbidities_regex, morbidities_namedict,
                             context_symptoms_regex, symptoms_namedict,
                             context_deseases_regex, deseases_namedict,
                             canonical_symptoms_name, canonical_comorb_names,
                             canonical_symptoms_order)
import re
import pandas as pd
import simplejson as json


class MedNotesMiner(object):
    """Medical notes data miner for Covid-19 insights"""
    def __init__(self, text_utf8, covid19_db=None, symptoms_db=None, sampling_db=None, morbidities_db=None):
        super(MedNotesMiner, self).__init__()
        self.wikidata_url = 'https://www.wikidata.org/wiki/'
        self.text = text_utf8
        self.clues = {'texto': self.text}
        self.lower_text = self.text.lower()
        if not covid19_db:
            self.covid19_db = covid19()
        if not symptoms_db:
            self.symptoms_db = wiki_symptoms()
        if not sampling_db:
            self.sampling_db = covid19_sampling()
        if not morbidities_db:
            self.morbidities_db = covid19_comorbidities()
        self.deseases_re = context_deseases_regex()
        self.deseases_dict = deseases_namedict()
        self.covid_re = context_covid_regex()
        self.covid_dict = covid_namedict()
        self.symptoms_re = context_symptoms_regex()
        self.symptoms_dict = symptoms_namedict()
        self.morbidities_re = context_morbidities_regex()
        self.morbidities_dict = morbidities_namedict()

    def check_covid19(self, lower_case=True):
        """match covid-19 mentions"""
        self.clues['COVID-19'] = {}

        # seek for covid matches
        for covid_mention in self.covid_re.finditer(self.lower_text):
            context_mention = '...'+(covid_mention.groups()[0]).replace('\n', ' ')+'...'
            name = covid_mention.groups()[2]
            key = self.covid_dict[name]
            info = {'descripción': covid_mention.groups()[2],
                            'mención': context_mention,
                            'wikidata': '{}{}'.format(self.wikidata_url, key)}

            if not key in self.clues['COVID-19']:
                self.clues['COVID-19'][key] = [info]
                continue

            self.clues['COVID-19'][key].append(info)

    def check_symptoms(self, lower_case=True):
        """match covid-19 symptoms"""
        self.clues['síntomas'] = {}

        # seek for symptoms matches
        for symptom_mention in self.symptoms_re.finditer(self.lower_text):
            context_mention = '...'+(symptom_mention.groups()[0]).replace('\n', ' ')+'...'
            symptom_name = symptom_mention.groups()[2]
            symptom_key = self.symptoms_dict[symptom_name]
            symptom_info = {'descripción': symptom_mention.groups()[2],
                            'mención': context_mention,
                            'wikidata': '{}{}'.format(self.wikidata_url, symptom_key)}

            if not symptom_key in self.clues['síntomas']:
                self.clues['síntomas'][symptom_key] = [symptom_info]
                continue

            self.clues['síntomas'][symptom_key].append(symptom_info)

    def check_comorbidities(self, lower_case=True):
        """match covid-19 comorbidities"""
        self.clues['comorbilidades'] = {}

        # seek for comorbidities matches
        for morbid_mention in self.morbidities_re.finditer(self.lower_text):
            context_mention = '...'+(morbid_mention.groups()[0]).replace('\n', ' ')+'...'
            morbid_name = morbid_mention.groups()[2]
            comorbidity_key = self.morbidities_dict[morbid_name]
            comorbidity_info = {'descripción': morbid_mention.groups()[2],
                                'mención': context_mention,
                                'wikidata': '{}{}'.format(self.wikidata_url, comorbidity_key)}

            if not comorbidity_key in self.clues['comorbilidades']:
                self.clues['comorbilidades'][comorbidity_key] = [comorbidity_info]
                continue

            self.clues['comorbilidades'][comorbidity_key].append(comorbidity_info)

    def check_sampling(self):
        """match covid-19 sampling mentions"""
        self.clues['muestreos'] = []

        # seek for sampling matches
        for sampling_cueword in self.sampling_db:
            regex = r'((\w+\W+){0,5}\b'+sampling_cueword+r'\b(\W+\w+){0,5})'
            for samp_mention in re.finditer(regex, self.lower_text):
                context_mention = '...'+(samp_mention.groups()[0]).replace('\n', ' ')+'...'
                self.clues['muestreos'].append({'mención': context_mention})


class CovidJsonParser(object):
    """Parse JSON symptoms registers generated by MedNotesMiner"""
    def __init__(self):
        # TODO: add 'fecha' as second column and all symptoms
        super(CovidJsonParser, self).__init__()
        self.symptoms = canonical_symptoms_name
        self.comorbs = canonical_comorb_names
        self.symptcols_order = canonical_symptoms_order

    def register_as_dict(self, medical_register):
        """depending on the object will open a file or not"""
        if isinstance(medical_register, dict):
            json_register = medical_register
        elif os.path.exists(medical_register):
            with open(medical_register) as fp:
                json_register = json.load(fp, encoding='utf-8')
        else:
            print(medical_register, 'KO')
            json_register = None
        return json_register

    def symptoms_occurrences(self, medical_register):
        """A binary presence/absence symptoms list"""
        json_register = self.register_as_dict(medical_register)

        presence_absence = [(self.symptoms[code], (code in json_register['síntomas']))
                            for code in self.symptcols_order]
        return presence_absence

    def comorbidities_dfval(self, medical_register):
        """return one single dataframe string value"""
        json_register = self.register_as_dict(medical_register)

        # list comorbidities by canonical names
        comorbs = ', '.join([self.comorbs[code] for (code,_) in json_register['comorbilidades'].items()])
        evidence = ''
        # TODO making work this
        #evidence = ', '.join([x['mención'] for x in comorb_list for c, comorb_list in json_register['comorbilidades'].items()]) 
        # for c, comorb_list in json_register['comorbilidades'].items():
        #     evidence = ', '.join([x['mención'] for x in comorb_list])
        return(comorbs, evidence)

    def covid_diagnosis_dfval(self, medical_register):
        """return diagnosis as single dataframe string value"""
        json_register = self.register_as_dict(medical_register)
        # list COVID-19 diagnosis found
        covid_diagnosis = []
        evidence = ''
        for (code, info) in json_register['COVID-19'].items():
            descriptions = [item['descripción'] for item in info]
            mentions = [item['mención'] for item in info]
            covid_diagnosis += list(set(descriptions))
            evidence += ', '.join(mentions)

        covid_diagnosis = ', '.join(covid_diagnosis)
        return(covid_diagnosis, evidence)

    def symptoms_dfval(self, medical_register):
        """return diagnosis as single dataframe string value"""
        json_register = self.register_as_dict(medical_register)

        # list symptoms found
        symptoms = []
        evidence = ''
        for (code, info) in json_register['síntomas'].items():
            descriptions = [item['descripción'] for item in info]
            mentions = [item['mención'] for item in info]
            symptoms += list(set(descriptions))
            evidence += ', '.join(mentions)

        symptoms = ', '.join(symptoms)
        return(symptoms, evidence)

    def dir_to_dataframe(self, jsons_inputdir):
        """Read a set of JSON by MedNotesMiner to form a pandas data frame"""

        registers = []
        for (MedNote_path, MedNote_bname) in explore_dir(jsons_inputdir, yield_extension='JSON'):
            d = {'No.': 1,
             'NHC': 325498,
             'Nombre (s)': 'Juan',
             'Apellido paterno': 'Pérez',
             'Apellido Materno': 'Gómez',
            }

            comorbs, comorbs_evidence = self.comorbidities_dfval(MedNote_path)
            d.update({'Comorbilidad': comorbs})

            covid_diagnosis, covid_diagnosis_evidence = self.covid_diagnosis_dfval(MedNote_path)
            d.update({'Diagnóstico': covid_diagnosis})
            # print(covid_diagnosis_evidence)

            symptoms, symptoms_evidence = self.symptoms_dfval(MedNote_path)
            d.update({'Síntomas': symptoms})
            # print(symptoms_evidence)
            registers.append(d)
        # create df
        df = pd.DataFrame(data=registers)
        print(df)
        return(df)

    def dir_to_csv(self, jsons_inputdir, sep=','):
        """Read a set of JSON by MedNotesMiner to form a symptoms table"""

        # header could be codes or names
        # header = sep.join(['nota','fecha'])+sep+(sep.join([code for code in self.symptcols_order]))
        header = sep.join(['nota','fecha'])+sep+(sep.join([self.symptoms[c] for c in self.symptcols_order]))
        table = header+'\n'
        date = '22/04/2020'
        # walk inputdir to get the csv rows
        for (MedNote_path, MedNote_bname) in explore_dir(jsons_inputdir, yield_extension='JSON'):
            id_note = MedNote_bname.split('.')[0].split('_')[1]
            try:
                presence_absence = [str(presence) for (sympt, presence) in self.symptoms_occurrences(MedNote_path)]
            except Exception as e:
                # This is because it may fail with some bad formated jsons.
                print(MedNote_path,'KO')
                # TODO continue in productions, sometimes a problem from OCR could arise
            presence_absence_str = sep.join(presence_absence)
            row = id_note+sep+date+sep+presence_absence_str
            table += row+'\n'
        return table


class OpenNLPTagger(object):
    """OpenNLP Tagger for diseases and symptoms based on long lists"""
    def __init__(self):
        super(OpenNLPTagger, self).__init__()
        self.symptoms_re = wiki_symptoms_regex()
        self.deseases_re = wiki_deseases_regex()
        self.tokenizer = Tokenizer()

    def tagbyreg(self, text, split_sents=False):
        """labelize symptoms and deseases ocurrences"""
        # depending on the object will open a file or not
        if isinstance(text, str):
            lower_text = text.lower()
        elif os.path.exists(text):
            with open(text, 'r', encoding='utf-8') as fp:
                lower_text = text.lower()
        else:
            print(text, 'KO')
            lower_text = None
        # prepare lines and tokens
        if split_sents:
            sentence_splitted = self.tokenizer.split_sentences(lower_text)
            tokenized = self.tokenizer.split_tokens(sentence_splitted)
        else:
            tokenized = self.tokenizer.split_tokens(lower_text)
        #  seek for symptoms and deaseses and tagg them
        labeled = self.deseases_re.sub(r'<START:Desease> \g<matched> <END>', tokenized)
        labeled = self.symptoms_re.sub(r'<START:Symptom> \g<matched> <END>', labeled)
        # correct nasty nested tags if produced
        nested =r'(?P<a><START:(Symptom|Desease)> (\w+ )*)<START:(Symptom|Desease)>(?P<b> (\w+ )+)<END>(?P<c> (\w+ )*<END>)'
        corrected_labeled = re.sub(nested, r'\g<a>\g<b>\g<c>', labeled)
        labeled_text = corrected_labeled.replace('  ',' ')
        return(labeled_text)


if __name__ == '__main__':

    corte_dir = HOME+"/data/corte_SEDESA_22_abril_2020/"
    parser = CovidJsonParser()
    # csv_symptoms = parser.dir_to_csv(corte_dir)
    # print(csv_symptoms)

    parser.dir_to_dataframe(corte_dir)

#     s = '''Durante los paroxismos de tos estos pacientes se tornan muy cianóticos y llegan incluso a quedar inconscientes .
# La tos de otros distintos tipos puede estar producida por la estimulación de terminaciones nerviosas situadas en la mucosa bronquial .
# La tos de la bronquitis aguda presenta características similares a la de la traqueítis , pero a menudo está precedida o acompañada por estertores transitorios y por una sensación de opresión difusa en el pecho .
# En los primeros momentos es seca ; fiando posteriormente se hace productiva , se transforma a la vez en suelta e indolora .
# La tos de la bronquitis crónica tiende a presentarse en paroxismos prolongados , que culminan casi siempre con la producción de esputo .
# Sin embargo , cuando éste es muy espeso o existe una alteración importante de la función ventilatoria , el paciente , agotado por los esfuerzos de la tos , puede cesar en sus esfuerzos por eliminar las secreciones bronquiales , y el episodio de tos concluye sin ningún resultado .
# Esta tos inconclusa , como la describen algunos pacientes , es típica de la bronquitis crónica avanzada .
# Los ataques de tos en estos pacientes a menudo producen disnea intensa , frecuentemente acompañada de estertores , y suelen ser muy penosos .
# La tos de la bronquitis crónica presenta otras características típicas ; es más frecuente e intensa cuando el paciente se acuesta , y aún más cuando se levanta por la mañana , debido los cambios bruscos de posición y a las variaciones en la temperatura del aire inspirado las que está expuesto en esos momentos .
# Raramente se ve interrumpido el sueño por alguna tos muy rara , pero la mayoría de los pacientes con bronquitis crónica se despiertan por la mañana con un ligero estertor y una sensación de opresión en el pecho , síntomas que no mejoran hasta que no se produce la expectoración mediante un violento taque de tos que puede prolongarse durante varios minutos .
# La tos de la bronquitis crónica se ve estimulada , además de por los cambios en la temperatura atmosférica , por irritantes bronquiales como el humo del tabaco , gases o polvo , y por el incremento súbito en la profundidad de las respiraciones producido por el ejercicio y por la risa .
# Algunos pacientes pueden sufrir un síncope por tos ( página 38 ) durante las crisis de tos prolongada y violenta .'''
#     tagger = OpenNLPTagger()
#     tagged = tagger.tagbyreg(s)
#     print(tagged)

