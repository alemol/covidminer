# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

from tmining.covid import MedNotesMiner
from tmining.ocr import TesseOCR

from flask import (Flask, request, jsonify, redirect, render_template, abort)

import os
import logging
from logging import Formatter, FileHandler
import simplejson as json
import urllib.request
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Globals
LANGUAGE = 'spa'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg'])

# For json's text encoding-decoding UTF-8
app.config['JSON_AS_ASCII']=False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp

@app.route('/covid19', methods=["POST"])
def covid19():
    logging.info('*covid19*')
    logging.info(request)
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
    else:
        resp = jsonify({'message' : 'Not Allowed file type'})
        resp.status_code = 400
        return resp

    # OCR stage
    my_ocr = TesseOCR(LANGUAGE)
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
    covid_symptoms = './resources/sintomas.csv'
    covid_sampling = './resources/muestras.txt'
    covid_seeker = MedNotesMiner(ocred_text,covid_symptoms,covid_sampling)
    try:
        covid_seeker.check_symptoms()
        covid_seeker.check_sampling()
        jsons =  json.dumps(covid_seeker.clues, ensure_ascii=False, encoding='utf-8', indent=2)
        return(jsons)
    except Exception as e:
        logging.info(e)
        abort(500)


@app.route('/ocr', methods=["POST"])
def ocr():
    try:
        logging.info('OCR LANGUAGE '+LANGUAGE)
        LANGUAGE = request.json['lang']
    except Exception as e:
        logging.info('OCR default language eng')
        LANGUAGE = 'eng'

    my_ocr = TesseOCR(LANGUAGE)

    try:
        url = request.json['image']
        if 'jpg' in url:
            logging.info(url)
            output = my_ocr.get_text(url)
            logging.info('OK')
            return({"text": output})
        else:
            return jsonify({"error": "only .jpg files, please"})
    except:
        abort(500)


@app.errorhandler(500)
def internal_error(error):
    logging.error(str(error))

# @app.errorhandler(404)
# def not_found_error(error):
#     logging.error(str(error))

# #if not app.debug:
file_handler = FileHandler('log/error.log')
file_handler.setFormatter(
    Formatter('%(asctime)s %(levelname)s: \
        %(message)s [in %(pathname)s:%(lineno)d]')
)

#logging.basicConfig(format='INFO: %(message)s', level=logging.INFO)
logging.basicConfig(format='INFO: %(message)s', level=logging.DEBUG)
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
