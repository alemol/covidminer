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

from c19mining.utils import (HOME, PLOTS_DIR, EXCELS_DIR, explore_dir,
                             canonical_symptoms_name, canonical_symptoms_order,
                             canonical_comorb_names, canonical_covid_name)

import numpy as np
import pandas as pd
import simplejson as json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from random import randint


class PlotGenerator(object):
    """Make Plots and data visualization"""
    def __init__(self, plots_dir=PLOTS_DIR):
        super(PlotGenerator, self).__init__()
        self.plots_dir = plots_dir
        self.symptom_names = [canonical_symptoms_name[code] for code in canonical_symptoms_order]

    def cooccurrences(self, data):
        """create a plot of cooccurrences of symptoms or comorbities"""

        # data could be DataFrame or the path to a csv table
        if isinstance(data, pd.DataFrame):
            df = data.loc[:, (data != False).any(axis=0)]
        elif os.path.exists(data):
            data_table = pd.read_csv(data, sep=',', parse_dates=True,
                dtype={'nota': np.string_, 'fecha':np.datetime64}.update({s: np.bool for s in self.symptom_names}))
            df = pd.DataFrame(columns=['nota', 'fecha']+self.symptom_names, data=data_table)
        else:
            print(data, 'KO')
            df = None
        # filter when columns with all False values
        df = df.loc[:, (df != False).any(axis=0)]
        symptoms = df.columns[2:]
        occurrences = df[symptoms].to_numpy()
        #print(df)
        self.cooccurrences_plot(symptoms, occurrences)

    def cooccurrences_plot(self, symptoms, occurrences, num_cooc=30, min_cooc_count=1, filename='cooccurrences_plot.jpg'):
        """create a plot of cooccurrences
        :param symptoms: list of S symptoms
        :param occurrences: NxS array of occurrences of each symptom for a list of N individuals
        :param num_cooc: number of cooccurrences to show, maximum would be 2**S - 1
        :param min_cooc_count: minimum count of cooccurrences needed to be shown in the plot
        """
        color='C1'
        num_symp = len(symptoms)
        symp_sums = occurrences.sum(axis=0)
        symp_order = symp_sums.argsort()
        inv_symp_order = symp_order.argsort()
        combinations = np.matmul(occurrences, (2 ** np.arange(num_symp))[inv_symp_order])
        bins = np.arange(1, 2 ** num_symp + 1)
        values, _ = np.histogram(combinations, bins=bins)
        cooc_order = (-values).argsort()
        num_cooc = np.minimum(num_cooc, len(np.where(values >= min_cooc_count)[0]))

        fig, axs = plt.subplots(2, 2, sharex='col', sharey='row', figsize=(10, 5),
                                gridspec_kw={'width_ratios': [1, 4], 'height_ratios': [2, 3],
                                             'wspace': 0.55, 'hspace': 0.25, 'left': 0.04, 'right': 0.9})
        for ax in axs.ravel():
            for dir in ['left', 'right', 'top', 'bottom']:
                ax.spines[dir].set_visible(False)
        axs[0, 0].axis('off')

        axs[0, 1].bar(range(num_cooc), values[cooc_order][:num_cooc], ec='white', color=color)
        axs[0, 1].tick_params(labelbottom=True, labelleft=True, length=0)
        axs[0, 1].tick_params(axis='x', rotation=90)
        axs[0, 1].grid(True, axis='y', ls='--')
        axs[0, 1].yaxis.set_major_locator(MaxNLocator(6))
        axs[0, 1].axhline(0, color=color)
        axs[0, 1].set_xlabel('Frecuencia de co-ocurrencias')


        axs[1, 0].barh(np.array(symptoms)[symp_order], symp_sums[symp_order], ec='white', color=color)
        axs[1, 0].tick_params(labelbottom=True, labelleft=False, left=False, length=0)
        axs[1, 0].invert_xaxis()
        axs[1, 0].grid(True, axis='x', ls='--')
        axs[1, 0].xaxis.set_major_locator(MaxNLocator(4))
        axs[1, 0].set_xlabel('Principales')

        ax = axs[1, 1]
        ax.tick_params(labelbottom=False, labelleft=True, length=0)
        ax.set_xticks(range(num_cooc))
        ax.set_xticklabels(values[cooc_order][:num_cooc])
        ax.set_xlim(-1, num_cooc - 0.4)
        for i, cooc in enumerate(bins[cooc_order][:num_cooc]):
            ax.plot(np.full(num_symp, i), np.arange(num_symp), 'ob-', alpha=0.15, color=color)
            occ = self.combined_number_to_list(cooc)
            ax.plot(np.full_like(occ, i), occ, 'ob-', color=color)
        axs[1, 1].set_xlabel('Co-ocurrencias')
        fig.suptitle('Frecuencia de síntomas y Co-ocurrencias de síntomas asociados a COVID-19 (N={}).'.format(len(occurrences)), fontsize=14)
        # TODO: no funciona bien format='eps'
        plt.savefig(os.path.join(HOME, self.plots_dir, filename))

    def combined_number_to_list(self, cooc):
        """convert a binary number to a list of its powers of two
           e.g. 5 is converted to [0, 2] because 5 == 2**0 + 2**2"""
        return [i for i in range(20) if cooc & (1 << i)]


class TableGenerator(object):
    """generates csv and Excel formated tables for COVID-19 report"""
    def __init__(self, excels_dir=EXCELS_DIR):
        super(TableGenerator, self).__init__()
        self.excels_dir = excels_dir
        self.symptoms = canonical_symptoms_name
        self.symptcols_order = canonical_symptoms_order
        self.comorbs = canonical_comorb_names

    def random_Ndigits(self, n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)

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
            evidence = '\n'.join([item['mención'] for item in decease])
        return evidence

    def dir_to_excel(self, jsons_inputdir, output='output.xlsx'):
        """Read a set of JSON by MedNotesMiner to form a excel"""
        concentrado  = list()
        evidencia    = list()
        for (MedNote_path, MedNote_bname) in explore_dir(jsons_inputdir, yield_extension='JSON'):
            
            main_info = {
                'NHC': self.random_Ndigits(6),
                'Nombre (s)':'',
                'Apellido paterno':'',
                'Edad':'',
                'Clave de la edad':'',
                'Sexo':'',
                'Fecha de Ingreso':'',
                '¿Se realizó prueba?':'',
                'Resultado de la prueba':'',
                'Estado o País':'',
                'Alcaldía o Municipio':'',
                'Fecha de alta':'',
                'Servicio (área donde está recibiendo atención el paciente)':'',
                'Traslado (movimiento interno de un servicio a otro)':'',
                'Clave Única de Establecimiento de Salud (CLUES)':'',
                'Motivo de la Alta':'',
                'Fecha de reingreso':'',
                'Observaciones':''
            }

            evidence_info = dict()

            medical_register = self.register_as_dict(MedNote_path)

            symptoms, symptoms_evidence = self.symptoms_to_val(medical_register)
            main_info.update({'Síntomas': symptoms})
            evidence_info.update({'Menciones Síntomas': symptoms_evidence})

            comorbs, comorbs_evidence = self.comorbidities_to_val(medical_register)
            main_info.update({'Comorbilidad': comorbs})
            evidence_info.update({'Menciones Comorbilidad': comorbs_evidence})

            covid_diagnosis, covid_diagnosis_evidence = self.covid_diagnosis_to_val(medical_register)
            main_info.update({'Diagnóstico': covid_diagnosis})
            evidence_info.update({'Menciones Diagnóstico': covid_diagnosis_evidence})

            samplings_evidence = self.sampling_to_val(medical_register)
            evidence_info.update({'Menciones Pruebas': samplings_evidence})

            decease_evidence = self.decease_to_val(medical_register)
            evidence_info.update({'Menciones Defunción': decease_evidence})

            # append register
            concentrado.append(main_info)
            evidencia.append(evidence_info)

        # create dfs
        df_concentrado = pd.DataFrame(data=concentrado)
        print(df_concentrado)
        df_evidencia = pd.DataFrame(data=evidencia)
        print(df_evidencia)

        # write excel
        with pd.ExcelWriter(output) as writer:
            df_concentrado.to_excel(writer, sheet_name='Concentrado 09052020')
            df_evidencia.to_excel(writer, sheet_name='Evidencia 09052020')

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



if __name__ == '__main__':

    corte_dir = HOME+"/data/corte_SEDESA_8_mayo/"
    table_gen = TableGenerator()

    # excel table report
    cut_directory = HOME+'/data/corte_SEDESA_8_mayo'    
    excel_created = table_gen.dir_to_excel(cut_directory)

    # csv table with symptoms coocurrences
    # csv_symptoms = table_gen.dir_to_csv(corte_dir)
    # print(csv_symptoms)
