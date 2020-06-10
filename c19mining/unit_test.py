# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

from c19mining.utils import (HOME, TEST_TEXT)
from c19mining.covid import MedNotesMiner
import os


class TestMedNotesMiner:

    def test_checkcovid19(self):
        textfile_path = os.path.join(HOME, TEST_TEXT)
        miner = MedNotesMiner(textfile_path)
        miner.check_covid19()
        miner.check_symptoms()
        miner.check_comorbidities()
        extracted_sections = miner.clues.keys()
        for section in ["texto", "COVID-19", "síntomas", "comorbilidades"]:
            assert section in extracted_sections

