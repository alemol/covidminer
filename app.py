# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

from c19mining.covid import MedNotesMiner
from c19mining.ocr import TesseOCR
from c19mining.utils import (uploads_dir, allowed_file, allowed_xml_file, log_file,
                             admissions_dir, discharges_dir, extractions_dir,
                             amcharts_dir, excels_dir)

import os
from os.path import join, exists
from datetime import datetime
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
    logging.info('* New xml urgencias requested *')
    logging.info('Receiving file ...')
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
    if file and allowed_xml_file(file.filename):
        logging.info(request.files)
        filename = secure_filename(file.filename)
        # creates datestamp dir an put the file there
        now = datetime.now()
        datestamp = now.strftime("%d_%m_%Y_%Hh%M")
        path_datestamp = join(app.config['XMLS_INGRESOS'], datestamp)
        if not exists(path_datestamp):
            os.makedirs(path_datestamp)
        file.save(join(app.config['XMLS_INGRESOS'], datestamp, filename))
        logging.info('xml file uploaded to server: OK')
    else:
        resp = jsonify({'message' : 'Not Allowed file type'})
        resp.status_code = 400
        return resp


@app.route('/upload', methods=['POST'])
def upload_file():
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
