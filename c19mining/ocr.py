# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas

import os
from os.path import (join, splitext, exists)
from c19mining.utils import (mkdir, explore_dir)
import pdf2image
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

class TesseOCR(object):
    """An Optical Character Recognition class based on tesseract"""
    def __init__(self, lang):
        super(TesseOCR, self).__init__()
        self.lang = lang if lang else 'eng'

    def get_text_from_pdf(self, pdf_path):
        """convert a pdf file into text"""
        text = ''
        images = pdf2image.convert_from_path(pdf_path)
        for pg, img in enumerate(images):
            text += pytesseract.image_to_string(img)
        return text

    def get_text_from_jpg(self, image_path):
        """convert a jpg image into text"""
        try:
            img = Image.open(image_path)
        except Exception as e:
            raise e
        text = pytesseract.image_to_string(img, lang=self.lang)
        return text

    def parse_book(self, book_path, out_text):
        mkdir(book_path, 'texts')
        for (image_page, fname) in explore_dir(book_path, yield_extension='jpg'):
            bname = splitext(fname)[0]
            text_path = join(out_text, 'texts', bname+'.txt')
            if exists(text_path):
                continue
            try:
                t = self.get_text_from_jpg(image_page)
            except Exception as e:
                t = ''

            if len(t) > 0:
                with open(text_path, 'w') as f:
                    f.write(t)
                print('Created', text_path)
