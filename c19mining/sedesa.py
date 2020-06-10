# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas
# 
# N.B : This is very specific for the hospital I am working on.
# 
# EXAMPLE of XML structure
# 
# <RESULTS>
#     <ROW>
#         <COLUMN NAME="CHN"><![CDATA[507314]]></COLUMN>
#         <COLUMN NAME="NAME"><![CDATA[ALEX]]></COLUMN>
#         <COLUMN NAME="SURNAME1"><![CDATA[MOLINA]]></COLUMN>
#         <COLUMN NAME="SURNAME2"><![CDATA[VILLEGAS]]></COLUMN>
#         <COLUMN NAME="INSERT_DATE"><![CDATA[30/03/20 15:46:20.668000000]]></COLUMN>
#         <COLUMN NAME="NOTA_INICIAL_URGENCIAS"><![CDATA[code code="1111-1" codeSystemName="LOINC" codeSystem="2.16.840.1.113883.2.38.1.10.1" displayName="LOINC Texto Libre" />
#           <title>Resultado de Escalas</title>
#           <text>No hay información para mostrar.</text>
#         </section>
#       </component>
#          ...
#         <section>
#           <code code="1111-1" codeSystemName="LOINC" codeSystem="2.16.840.1.113883.2.38.1.10.1" displayName="LOINC Texto Libre" />
#           <title>Resumen de Interrogatorio, Exploración Física y/o Estado Mental</title>
#           <text>SE TRAT DE MASCULINO DE 41 AÑOS DE EDAD QUE ACUDE ...</text>
#         </section>]]></COLUMN>
#     </ROW>
#     ...

import sys
import os
from os.path import (join, dirname, exists)
sys.path.append(join(dirname(__file__), ".", ".."))

from c19mining.covid import MedNotesMiner
from c19mining.utils import extractions_dir

import re
import simplejson as json
from bs4 import BeautifulSoup
from datetime import datetime

class XMLParser(object):
    """docstring for XMLParser"""
    def __init__(self, inputxml):
        super(XMLParser, self).__init__()
        self.extractions_dir = extractions_dir()
        infile = open(inputxml, 'r')
        contents = infile.read()
        self.xmlsoup = BeautifulSoup(contents, 'xml')

    def count_valid_records(self, expected_fields):
        """Count how many records are readable (valid)"""
        counter = 0
        for row in self.xmlsoup.find_all('ROW'):
            fields = [col for col in row.find_all('COLUMN')]
            if len(fields) == expected_fields:
                counter += 1
        return counter

    def datestamps(self):
        stamps = dict()
        for row in self.xmlsoup.find_all('ROW'):
            fields = [col for col in row.find_all('COLUMN')]
            for f in fields:
                m = re.search('INSERT_DATE', str(f))
                if m:
                    t = f.get_text()
                    date_str = t.split(' ')[0]
                    time_str = t.split(' ')[1]
                    date = datetime(int(date_str.split('/')[2]),
                                    int(date_str.split('/')[1]),
                                    int(date_str.split('/')[0]),
                                    )
                    if date in stamps.keys():
                        stamps[date]+= 1
                    else:
                        stamps[date] = 1        
        return stamps

    def covid_extraction(self, outputdir=None):
        """Read each record from an XML to extract covid insights"""
        for row in self.xmlsoup.find_all('ROW'):
        # it could fail for a particular row because XML is dirty
            try:
                (chn, name, surname1, surname2, 
                insert_data, nota_inicial_urgencias) = (col.get_text() 
                for col in row.find_all('COLUMN'))
                # clean tags inside pseudo-free text
                soup = BeautifulSoup(nota_inicial_urgencias)
                notags_text = re.sub(r"<.*?>", " ", nota_inicial_urgencias)
                # TODO: dirty lines from SEDESA XML
                # print(notags_text)
                # Information Extraction on free text
                covid_seeker = MedNotesMiner(notags_text,
                    {'NHC': chn,
                     'Nombre': name,
                     'Apellido Paterno':surname1,
                     'Apellido Materno': surname2,
                     'Fecha de Ingreso': insert_data
                    })
                covid_seeker.check_covid19()
                covid_seeker.check_symptoms()
                covid_seeker.check_sampling()
                covid_seeker.check_decease()
                covid_seeker.check_comorbidities()
                covid_insights =  json.dumps(covid_seeker.clues, ensure_ascii=False, encoding='utf-8', indent=2)
                print(covid_insights)
                # store extractions into JSON files
                if not exists(outputdir):
                    os.makedirs(outputdir)
                # store into a JSON file
                fname = 'NHC_{}_{}_Cabrera'.format(chn, (insert_data.split(' ')[0]).replace('/',''))
                inserver_path = join(outputdir, fname+'.JSON')
                with open(inserver_path, 'w') as wf:
                    wf.write(covid_insights)
            except ValueError as e:
                continue

if __name__ == '__main__':
    inputxml = sys.argv[1]

    # parse XML 
    xmlparser = XMLParser(inputxml)
    stamps = xmlparser.datestamps()
