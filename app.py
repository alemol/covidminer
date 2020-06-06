# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

from c19mining.sedesa import XMLParser
from c19mining.covid import MedNotesMiner
from c19mining.report import ReportGenerator
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


@app.route('/urgencias', methods=['POST'])
def upload_xml_urgencias():
    datestamp = get_time()
    logging.info('* New xml urgencias request: {} *'.format(datestamp))
    # check if the post request has the xml file an upload it
    uploaded_file = upload_check(request)
    if not uploaded_file:
        resp = jsonify({'message' : 'Not a valid file in the request'})
        resp.status_code = 400
        logging.info('Upload xml KO')
        return resp
    logging.info('Upload xml OK')
    # copy file to app server
    stored_xml_file = store_uploaded_file(uploaded_file, datestamp)
    if not stored_xml_file:
        resp = jsonify({'message' : 'Error copying the file on server'})
        resp.status_code = 500
        logging.info('Store xml KO')
        return resp
    logging.info('Store xml OK')
    # extract covid insights from XML
    logging.info('Mining COVID-19 information ...')
    #xmlparser = XMLParser(stored_xml_file)
    #xmlparser.covid_extraction(outputdir=join(app.config['EXTRACTIONS_DATA'], datestamp))
    logging.info('Mined COVID-19 information OK')
    # build a excel report for all notes in a directory
    logging.info('Writing excel report ...')
    report = ReportGenerator(mednotes_dir=join(app.config['EXTRACTIONS_DATA'], datestamp),
                             excels_dir=join(app.config['EXCEL_DATA'], datestamp),
                             only_covid=False)
    report.to_excel()
    logging.info('Writen excel report OK')
    # DONE!
    resp = jsonify({'message' : 'OK'})
    resp.status_code = 200
    return resp

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

def store_uploaded_file(uploaded_file, datestamp):
    logging.info('Storing xml ...')
    fname = secure_filename(uploaded_file.filename)
    path_datestamp = join(app.config['XMLS_INGRESOS'], datestamp)
    if not exists(path_datestamp):
        os.makedirs(path_datestamp)
    inserver_path = join(app.config['XMLS_INGRESOS'], datestamp, fname)
    uploaded_file.save(inserver_path)
    if exists(inserver_path):
        logging.info('"{}"'.format(inserver_path))
        return inserver_path
    else:
        return None


@app.route('/upload', methods=['POST'])
def upload_any_file():
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
        resp = jsonify({'message' : 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message' : 'Not Allowed file type'})
        resp.status_code = 400
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
    logging.info('OCR ...')
    try:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if 'pdf' in pdf_path:
            logging.info(pdf_path)
            ocred_text = my_ocr.get_text_from_pdf(pdf_path)
            logging.info('OCR OK')
        else:
            return jsonify({"error": "only .pdf files, please"})
    except:
        abort(500)

    # symptoms stage
    covid_seeker = MedNotesMiner(ocred_text)
    try:
        covid_seeker.check_covid19()
        covid_seeker.check_symptoms()
        covid_seeker.check_sampling()
        covid_seeker.check_decease()
        covid_seeker.check_comorbidities()
        jsons =  json.dumps(covid_seeker.clues, ensure_ascii=False, encoding='utf-8', indent=2)
        logging.info('OCR OK')
        logging.info('Text Mining OK')
        return(jsons)
    except Exception as e:
        logging.info(e)
        abort(500)

@app.route('/ocr', methods=["POST"])
def ocr():
    logging.info('*OCR request.files*')
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
    logging.info('OCR ...')
    try:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if 'pdf' in pdf_path:
            logging.info(pdf_path)
            ocred_text = my_ocr.get_text_from_pdf(pdf_path)
            logging.info('OCR OK')
        else:
            return jsonify({"error": "only .pdf files, please"})
    except:
        abort(500)

    return ocred_text

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
