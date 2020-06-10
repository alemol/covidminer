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

from c19mining.utils import (wiki_deseases_regex, wiki_symptoms_regex, drugs_regex)
import re
from os.path import exists
from mosestokenizer import *

import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
from nltk import word_tokenize


class Tokenizer(object):
    """tokenize detokenize and split sentsences from text"""
    def __init__(self, lang='es'):
        super(Tokenizer, self).__init__()
        self.lang = lang

    def split_tokens(self, text):
        """Apply tokenization split, e.g.
        ...la parte de arriba son superiores ( craneales , rostrales ) , y las ...
        """
        contents = self.list_of_str(text)
        tokens = ''
        for line in contents:
            if line == '\n':
                tokens += '\n'
            else:
                tokens += '{}\n'.format(' '.join(word_tokenize(line)))
        return tokens

    def join_tokens(self, text):
        """Undo what split_tokens does, e.g.
        ...la parte de arriba son superiores (craneales,rostrales), y las ...
        """
        contents = self.list_of_tokens(text)
        with MosesDetokenizer(self.lang) as detokenize:
            detokenized = '\n'.join([detokenize(tokens) for tokens in contents])
        return detokenized

    def split_sentences(self, text):
        """Detect sentence limits and add newline characters"""
        contents = self.list_of_str(text)
        with MosesSentenceSplitter('es') as splitsents:
            sentences = ''
            for line in contents:                
                if line == '' or re.match(r'\s+', line):
                    sentences +='\n'
                else:
                    sentences += '\n'.join(splitsents([line]))+'\n'
        return sentences

    def list_of_str(self, text):
        """return a list of strings regardless the input object type"""
        if exists(text):
            with open(text, 'r') as f:
                contents = f.readlines()
        elif isinstance(text, str):
            contents = text.split('\n')
        return contents

    def list_of_tokens(self, text):
        """return a list of list of tokens regardless the input object type"""
        if exists(text):
            with open(text, 'r') as f:
                contents = [line.split() for line in f.readlines()]
        elif isinstance(text, str):            
            contents = [(l+'\n').split() for l in text.split('\n')]
        return contents


class OpenNLPTagger(object):
    """OpenNLP Tagger for diseases and symptoms based on long lists"""
    def __init__(self):
        super(OpenNLPTagger, self).__init__()
        self.symptoms_re = wiki_symptoms_regex()
        self.deseases_re = wiki_deseases_regex()
        self.drugs_re = drugs_regex()
        self.tokenizer = Tokenizer()

    def tagbyreg(self, text, split_sents=False):
        """labelize symptoms and deseases ocurrences"""
        # depending on the object will open a file or not

        if os.path.exists(text):
            with open(text, 'r', encoding='utf-8') as fp:
                lower_text = (fp.read()).lower()
        else:
            print(text, 'KO')
            lower_text = None

        # prepare lines and tokens
        if split_sents:
            sentence_splitted = self.tokenizer.split_sentences(lower_text)
            tokenized = self.tokenizer.split_tokens(sentence_splitted)
        else:
            tokenized = self.tokenizer.split_tokens(lower_text)
        #  seek for symptoms and deaseses and tagg them
        labeled = self.deseases_re.sub(r'<START:Desease> \g<matched> <END>', tokenized)
        labeled = self.symptoms_re.sub(r'<START:Symptom> \g<matched> <END>', labeled)
        labeled = self.drugs_re.sub(r'<START:Drug> \g<matched> <END>', labeled)
        # correct nasty nested tags if produced
        nested =r'(?P<a><START:(Symptom|Desease|Drug)> (\w+ )*)<START:(Symptom|Desease|Drug)>(?P<b> (\w+ )+)<END>(?P<c> (\w+ )*<END>)'
        corrected_labeled = re.sub(nested, r'\g<a>\g<b>\g<c>', labeled)
        labeled_text = corrected_labeled.replace('  ',' ')
        return(labeled_text)


if __name__ == '__main__':

    input_string_nosents = '''INTRODUCCIÓN POSICIÓN ANATÓMICA
    La posición anatómica, según la cual se orientan las relaciones anatómicas, es aquella en la que el sujeto está de pie, con los pies juntos, los ojos mirando al frente y los brazos caídos a lo largo de los lados del cuerpo, con las palmas orientadas al frente. Las estructuras situadas en la cara delantera se llaman anteriores (ventrales), y las de detrás, posteriores (dorsales).Una excepción a esta regla es el pie, que sufre una rotación interna durante el desarrollo: la cara inferior (plantar) se considera ventral, y la superior, dorsal.En relación con la línea media, las estructuras pueden estar más cerca (mediales) o más lejos (laterales), aquellas situadas en la línea media se denominan mediales.Las estructuras de la parte de arriba son superiores (craneales, rostrales), y las de la parte de abajo son inferiores (caudales).Un plano sagital pasa verticalmente, en dirección anteroposterior a través del cuerpo (el plano sagital medio está situado en la línea media).Un plano coronal es aquél que corta en ángulo recto, en dirección vertical al plano sagital.Un plano transversal (u horizontal) pasa horizontalmente a través del cuerpo. Los términos proximal y distal indican la relación de una estructura con el centro del cuerpo: la muñeca es proximal a la mano y el tobillo es distal a la rodilla.'''

    t = Tokenizer()
    # before split
    print(input_string_nosents)

    sentence_splitted = t.split_sentences(input_string_nosents)
    # after split
    print(sentence_splitted)

    tok_splitted = t.split_tokens(sentence_splitted)
    # after tokenization
    print(tok_splitted)

    tok_joined = t.join_tokens(tok_splitted)
    #after detokenization
    print(tok_joined)

    
    tagger = OpenNLPTagger()
    tagged = tagger.tagbyreg(tok_splitted)
    print(tagged)
