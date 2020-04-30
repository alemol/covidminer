# -*- coding: utf-8 -*-
#
# Created by Alex Molina
# April 2020
# 
# This project is licensed under the MIT License - see the LICENSE file for details.
# Copyright (c) 2020 Alejandro Molina Villegas


import re
import os
from os.path import exists
from mosestokenizer import *


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
        #Moses tokenization
        with MosesTokenizer(self.lang) as tokenize:
            tokens = ''
            for line in contents:
                if line == '\n':
                    tokens += '\n'
                else:
                    tokens += '{}\n'.format(' '.join(tokenize(line)))
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
                if re.match(r'\s*\n',line):
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
