# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas


from c19mining.sedesa import XMLParser
from c19mining.covid import MedNotesMiner
from c19mining.report import ReportGenerator, AmchartsGenerator
from c19mining.ocr import TesseOCR
from c19mining.utils import (uploads_dir, allowed_file, allowed_xml_file, log_file,
                             admissions_dir, discharges_dir, extractions_dir,
                             amcharts_dir, excels_dir, get_time)

import os
from os.path import join, exists
import logging
from logging import Formatter, FileHandler
import simplejson as json
import urllib.request
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, redirect, render_template, abort
import threading
from glob import glob


app = Flask(__name__)

# App Globals
LANGUAGE = 'spa'
app.config['JSON_AS_ASCII'] = False
app.config['XMLS_INGRESOS'] = admissions_dir()
app.config['XMLS_EGRESOS'] = discharges_dir()
app.config['EXTRACTIONS_DATA'] = extractions_dir()
app.config['AMCHARTS_DATA'] = amcharts_dir()
app.config['EXCEL_DATA'] = excels_dir()
app.config['UPLOAD_FOLDER'] = uploads_dir()
my_ocr = TesseOCR(LANGUAGE)


@app.route('/ingresos', methods=['POST'])
def upload_xml_ingresos():
    datestamp = get_time()
    logging.info('* New xml ingresos request: {} *'.format(datestamp))
    # check if the post request has the xml file an upload it
    uploaded_file = upload_check(request)
    if not uploaded_file:
        resp = jsonify({'message' : 'Not a valid file in the request'})
        resp.status_code = 400
        logging.info('Upload xml KO')
        return resp
    logging.info('Upload xml OK')
    # copy file to app server
    stored_xml_file = store_uploaded_file(uploaded_file, app.config['XMLS_INGRESOS'], datestamp)
    if not stored_xml_file:
        resp = jsonify({'message' : 'Error copying the file on server'})
        resp.status_code = 500
        logging.info('Store xml KO')
        return resp
    logging.info('Stored xml OK')
    # count valid records
    xmlparser = XMLParser(stored_xml_file)
    valid = xmlparser.count_valid_records(6)
    # extract covid insights from XML in the background
    # task_thread = threading.Thread(target=xmlparser.covid_extraction,
    #     name='Thread-covid_{}'.format(datestamp),
    #     kwargs={'outputdir': join(app.config['EXTRACTIONS_DATA'], datestamp)})
    # task_thread.start()
    # success
    resp = jsonify({'xml_ingresos' : stored_xml_file,
                    'valid_records': valid})
    resp.status_code = 200
    return resp

@app.route('/egresos', methods=['POST'])
def upload_xml_egresos():
    datestamp = get_time()
    logging.info('* New xml egresos request: {} *'.format(datestamp))
    # check if the post request has the xml file an upload it
    uploaded_file = upload_check(request)
    if not uploaded_file:
        resp = jsonify({'message' : 'Not a valid file in the request'})
        resp.status_code = 400
        logging.info('Upload xml KO')
        return resp
    logging.info('Upload xml OK')
    # copy file to app server
    stored_xml_file = store_uploaded_file(uploaded_file, app.config['XMLS_EGRESOS'], datestamp)
    if not stored_xml_file:
        resp = jsonify({'message' : 'Error copying the file on server'})
        resp.status_code = 500
        logging.info('Store xml KO')
        return resp
    logging.info('Stored xml OK')
    # count valid records
    xmlparser = XMLParser(stored_xml_file)
    valid = xmlparser.count_valid_records(7)
    # success
    resp = jsonify({'xml_egresos' : stored_xml_file,
                    'valid_records': valid})
    resp.status_code = 200
    return resp

@app.route('/textmining', methods=['POST'])
def textmining():
    datestamp = get_time()
    # extract covid insights from XML in the background
    admissions_xml = find_xml(app.config['XMLS_INGRESOS'], datestamp)
    xmlparser = XMLParser(admissions_xml)
    thread_name ='Thread-covid_{}'.format(datestamp)
    extractions_dir = join(app.config['EXTRACTIONS_DATA'], datestamp)
    task_thread = threading.Thread(target=xmlparser.covid_extraction,
        name='Thread-covid_{}'.format(datestamp),
        kwargs={'outputdir': extractions_dir})
    task_thread.start()
    # success
    resp = jsonify({'thread' : thread_name,
                    'extracciones': extractions_dir})
    resp.status_code = 200
    return resp

@app.route('/reporte', methods=['POST'])
def build_report():
    datestamp = get_time()
    report = ReportGenerator(mednotes_dir=join(app.config['EXTRACTIONS_DATA'], datestamp),
                             excels_dir=join(app.config['EXCEL_DATA'], datestamp),
                             only_covid=True)
    report.to_excel()
    logging.info('Writen excel report OK')
    # data creation for charts
    chart_dir = join(app.config['AMCHARTS_DATA'], datestamp)
    amchart_gen = AmchartsGenerator()
    am_symptoms = amchart_gen.pictorial_stacked_chart(report.df_symptoms, 10)
    logging.info(am_symptoms)
    am_comorbs = amchart_gen.pictorial_stacked_chart(report.df_comorbs, 10)
    logging.info(am_comorbs)
    # admissions and discharges
    admissions_xml = find_xml(app.config['XMLS_INGRESOS'], datestamp)
    xml_admissions = XMLParser(admissions_xml)
    admissions_stamps = xml_admissions.datestamps()
    #logging.info(admissions_stamps)
    discharges_xml = find_xml(app.config['XMLS_EGRESOS'], datestamp)
    #logging.info('discharges xml', discharges_xml)
    xml_discharges = XMLParser(discharges_xml)
    discharges_stamps = xml_discharges.datestamps()
    #logging.info(discharges_stamps)
    am_pyramid = amchart_gen.population_pyramid(admissions_stamps, discharges_stamps)
    logging.info(am_pyramid)
    # store data for charts
    symp_path = write_chart_data(am_symptoms, chart_dir, 'am_symptoms.JSON')
    comorbs_path = write_chart_data(am_comorbs, chart_dir, 'am_comorbs.JSON')
    pyramid_path = write_chart_data(am_pyramid, chart_dir, 'am_pyramid.JSON')
    # DONE!
    resp = jsonify({'excel' : join(app.config['EXCEL_DATA'], datestamp, 'informe_de_covid_'+datestamp+'.xlsx'),
                    'symptoms' : symp_path,
                    'comorbs' : comorbs_path,
                    'ingresos_egresos': pyramid_path
                    })
    resp.status_code = 200
    return resp

@app.route('/covid19', methods=["POST"])
def covid19():
    logging.info('*covid19 request.files*')
    logging.info('Receiving file ...')
    logging.info(request.files)
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        logging.info('File OK')
    else:
        resp = jsonify({'message' : 'Not Allowed file type'})
        resp.status_code = 400
        return resp

    # OCR stage
    try:
        f_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if 'pdf' in f_path:
            logging.info(f_path)
            logging.info('OCR ...')
            text = my_ocr.get_text_from_pdf(f_path)
            logging.info('OCR OK')
        elif 'txt' in f_path:
            with open(f_path, 'r') as f:
                text = f.read()
        else:
            return jsonify({"error": "only .pdf or .txt files can be processed."})
    except:
        abort(500)

    # symptoms stage
    covid_seeker = MedNotesMiner(text)
    try:
        covid_seeker.check_covid19()
        covid_seeker.check_symptoms()
        covid_seeker.check_sampling()
        covid_seeker.check_decease()
        covid_seeker.check_comorbidities()
        json_resp =  json.dumps(covid_seeker.clues, ensure_ascii=False, encoding='utf-8', indent=2)
        logging.info('Text Mining OK')
        return(json_resp)
    except Exception as e:
        logging.info(e)
        abort(500)

def upload_check(request):
    logging.info('Uploading xml ...')
    if 'file' not in request.files:
        return None
    file = request.files['file']
    fname = file.filename
    if fname == '':
        return None
    if not allowed_xml_file(fname):
        return None
    return file

def store_uploaded_file(uploaded_file, upload_directory, datestamp):
    logging.info('Storing xml ...')
    fname = secure_filename(uploaded_file.filename)
    path_datestamp = join(upload_directory, datestamp)
    if not exists(path_datestamp):
        os.makedirs(path_datestamp)
    inserver_path = join(upload_directory, datestamp, fname)
    uploaded_file.save(inserver_path)
    if exists(inserver_path):
        logging.info('"{}"'.format(inserver_path))
        return inserver_path
    else:
        return None

def write_chart_data(data, chart_dir, data_fname):
    if not exists(chart_dir):
        os.makedirs(chart_dir)
    json_data_path = join(chart_dir, data_fname)
    f = open(json_data_path, 'w')
    json.dump(data, f)
    f.close()
    return json_data_path

def find_xml(dir_xmls, datestamp):
    stamped_dir = join(dir_xmls, datestamp)
    xml_path = glob(stamped_dir+'/*xml')[0]
    return xml_path

@app.errorhandler(500)
def internal_error(error):
    logging.error(str(error))

@app.errorhandler(404)
def not_found_error(error):
    logging.error(str(error))

if not app.debug:
    log = log_file()
    file_handler = FileHandler(log)
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: \
            %(message)s [in %(pathname)s:%(lineno)d]'))

#logging.basicConfig(format='INFO: %(message)s', level=logging.INFO)
logging.basicConfig(format='INFO: %(message)s', level=logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
