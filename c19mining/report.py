# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

import sys
import os
from os.path import (join, dirname, exists)
sys.path.append(join(dirname(__file__), ".", ".."))

from c19mining.utils import (HOME, EXCELS_DIR, explore_dir,
                             canonical_symptoms_name, canonical_symptoms_order,
                             canonical_comorbs_name, canonical_comorbs_order,
                             canonical_covid_name, get_time)
import string
import pandas as pd
import simplejson as json
from collections import Counter


class ReportGenerator(object):
    """creates a report from all medical notes in a directory"""
    def __init__(self, mednotes_dir, excels_dir=EXCELS_DIR, only_covid=False):
        super(ReportGenerator, self).__init__()
        self.mednotes_dir = mednotes_dir
        self.excels_dir = excels_dir
        self.only_covid = only_covid
        self.symptoms = canonical_symptoms_name()
        self.symptcols_order = canonical_symptoms_order()
        self.comorbs = canonical_comorbs_name()
        self.comorbscols_order = canonical_comorbs_order()
        self.data_frames()

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

    def data_frames(self, only_covid=False):
        main_report = list()
        evidence = list()
        symptomsl = list()
        comorbis = list()
        for (MedNote_path, MedNote_bname) in explore_dir(self.mednotes_dir, yield_extension='JSON'):
            evidence_info = dict()
            sympt_info = dict()
            comorbs_info = dict()

            medical_register = self.register_as_dict(MedNote_path)
            # If report must include only COVID detected
            if (self.only_covid and len(medical_register['COVID-19']) == 0):
                continue

            main_info = {'NHC': medical_register['NHC'],
            'Nombre (s)': medical_register['Nombre'],
                'Apellido paterno': medical_register['Apellido Paterno'],
                'Apellido Materno': medical_register['Apellido Materno'],
                'Fecha de Ingreso':medical_register['Fecha de Ingreso'],
                'Servicio': 'Urgencias'}

            symptoms, symptoms_evidence = self.symptoms_to_val(medical_register)
            main_info.update({'Síntomas': symptoms})
            evidence_info.update({'Menciones Síntomas': symptoms_evidence})

            covid_diagnosis, covid_diagnosis_evidence = self.covid_diagnosis_to_val(medical_register)
            main_info.update({'Diagnóstico COVID-19': covid_diagnosis})
            evidence_info.update({'Menciones Diagnóstico': covid_diagnosis_evidence})

            comorbs, comorbs_evidence = self.comorbidities_to_val(medical_register)
            main_info.update({'Comorbilidad': comorbs})
            evidence_info.update({'Menciones Comorbilidad': comorbs_evidence})

            samplings_evidence = self.sampling_to_val(medical_register)
            evidence_info.update({'Menciones Pruebas': samplings_evidence})

            decease_evidence = self.decease_to_val(medical_register)
            evidence_info.update({'Menciones Defunción': decease_evidence})

            # symptoms boolean matrix
            sympt_info.update({self.symptoms[code]: (True if code in medical_register['síntomas'] else False)
             for code in self.symptcols_order})
            # comorbs boolean matrix
            comorbs_info.update({self.comorbs[code]: (True if code in medical_register['comorbilidades'] else False)
             for code in self.comorbscols_order})

            # append register
            main_report.append(main_info)
            evidence.append(evidence_info)
            symptomsl.append(sympt_info)
            comorbis.append(comorbs_info)

        # create dfs
        self.df_report = pd.DataFrame(data=main_report)
        self.df_symptoms = pd.DataFrame(data=symptomsl)
        self.df_comorbs = pd.DataFrame(data=comorbis)
        self.df_evidence = pd.DataFrame(data=evidence)

    def to_excel(self, out_directory=None):
        """Read a set of JSON by MedNotesMiner to form a excel"""

        # path to generated excel
        if not exists(self.excels_dir):
            os.makedirs(self.excels_dir)
        dt_string = get_time()
        out_directory = out_directory if out_directory else self.excels_dir
        output = join(out_directory, 'informe_de_covid_'+dt_string+'.xlsx')

        # write excel file
        try:
            with pd.ExcelWriter(output) as writer:
                self.df_report.to_excel(writer, sheet_name='Concentrado '+'marzo-mayo-2020')
                self.df_evidence.to_excel(writer, sheet_name='Evidencia '+'marzo-mayo-2020')
                self.df_symptoms.to_excel(writer, sheet_name='síntomas '+'marzo-mayo-2020')
                self.df_comorbs.to_excel(writer, sheet_name='Comorbilidad'+'marzo-mayo-2020')
                # set shit width
                self.set_width(writer, 'Concentrado marzo-mayo-2020', 'B', 'V', 30)
                self.set_width(writer, 'Evidencia marzo-mayo-2020', 'B', 'F', 40)
        except Exception as e:
            raise e

    def comorbidities_to_val(self, json_register):
        """return one single dataframe string value"""
        # list comorbidities by canonical names
        comorbs = '\n'.join([self.comorbs[code] for (code,_) in json_register['comorbilidades'].items()])
        evidence = ''
        # list COVID-19 comorbidities found
        comorbidities = []
        evidence = ''
        for (code, info) in json_register['comorbilidades'].items():
            descriptions = [item['descripción'] for item in info]
            mentions = [item['mención'] for item in info]
            comorbidities += list(set(descriptions))
            evidence += '\n'.join(mentions)

        comorbidities = '\n'.join(comorbidities)
        return(comorbidities, evidence)

    def covid_diagnosis_to_val(self, json_register):
        """return diagnosis as single dataframe string value"""
        # list COVID-19 diagnosis found
        covid_diagnosis = []
        evidence = ''
        for (code, info) in json_register['COVID-19'].items():
            descriptions = [item['descripción'] for item in info]
            mentions = [item['mención'] for item in info]
            covid_diagnosis.append(code)
            evidence += '\n'.join(mentions)

        covid_diagnosis = '\n'.join([canonical_covid_name[code] for code in list(set(covid_diagnosis))])
        return(covid_diagnosis, evidence)

    def symptoms_to_val(self, json_register):
        """return diagnosis as single dataframe string value"""
        # list symptoms found
        symptoms = []
        evidence = ''
        for (code, info) in json_register['síntomas'].items():
            descriptions = [item['descripción'] for item in info]
            mentions = [item['mención'] for item in info]
            symptoms += list(set(descriptions))
            evidence += '\n'.join(mentions)

        symptoms = '\n'.join(symptoms)
        return(symptoms, evidence)

    def sampling_to_val(self, json_register):
        samplings = json_register['muestreos']
        if len(samplings) == 0:
            evidence = ''
        else:
            evidence = '\n'.join([item['mención'] for item in samplings])
        return evidence

    def decease_to_val(self, json_register):
        deceases = json_register['defunciones']
        if len(deceases) == 0:
            evidence = ''
        else:
            evidence = '\n'.join([item['mención'] for item in deceases])
        return evidence

    def set_width(self, writer, sheet_name, start, end, dwidth):
        charmap = [c for c in list(string.ascii_uppercase) if (ord(c)>=ord(start) and ord(c)<=ord(end))]
        for char in charmap:
            writer.sheets[sheet_name].column_dimensions[char].width = dwidth


class AmchartsGenerator(object):
    """Data frames into Amcharts data formats"""
    def __init__(self):
        super(AmchartsGenerator, self).__init__()

    def pictorial_stacked_chart(self, df, topn=5):
        """https://www.amcharts.com/demos/pictorial-stacked-chart/"""
        counts = df[df==True].count(axis=0)
        dic_counts = Counter(counts.to_dict())
        chart_data = [{"name": k, "value": v} for k,v in dic_counts.most_common(topn)]
        return chart_data

if __name__ == '__main__':
    # cut_directory = HOME+'/data/corte_SEDESA_13_mayo'
    notes_directory = sys.argv[1]

    # build a excel report for all notes in a directory
    report = ReportGenerator(notes_directory)
    report.to_excel()

    # data for amChart
    amchart_gen = AmchartsGenerator()
    am_symptoms = amchart_gen.pictorial_stacked_chart(report.df_symptoms, 10)
    print(am_symptoms)
    am_comorbs = amchart_gen.pictorial_stacked_chart(report.df_comorbs, 10)
    print(am_comorbs)
