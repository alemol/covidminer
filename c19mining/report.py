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

from c19mining.utils import HOME, PLOTS_DIR, canonical_symptoms_name, canonical_symptoms_order

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


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


class ExcelGenerator(object):
    """generates Excel table for daily COVID-19 report"""
    def __init__(self, excels_dir=EXCELS_DIR):
        super(ExcelGenerator, self).__init__()
        self.excels_dir = excels_dir

    def build_report(JSONS_dir):
        """creates the excel file from all JSONS"""
        pass


if __name__ == '__main__':

    # symptoms report
    csv_path = HOME+'/data/cooccurrences_of_symptoms.csv'
    plot_gen = PlotGenerator()
    plot_gen.cooccurrences(csv_path)

    # excel table report
    cut_directory = HOME+'data/corte_SEDESA_22_abril_2020'
    excel_gen = ExcelGenerator()
    excel_gen.build_report(cut_directory)

