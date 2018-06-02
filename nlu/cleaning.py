#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import os
import codecs

from maxbot.configuration import stopword_file

ACCENTS = {'á': 'a',
           'é': 'e',
           'í': 'i',
           'ó': 'o',
           'ú': 'u'}

def remove_accents(phrase):
    """Simple Spanish accent remover.
    """
    new = phrase
    for acc, non in ACCENTS.items():
        new = new.replace(acc, non)
        new = new.replace(acc.upper(), non.upper())
    return new

class NLCleaner:
    """A natural language cleaner, based in stopwords.
    Stemming should be added soon!
    """

    def __init__(self, stopwords=stopword_file):
        assert os.path.exists(stopwords)
        self.stopw_regex = []
        self.stopwords = []
        with codecs.open(stopwords, 'r', encoding='utf-8') as f:
            lines = [l.encode('utf-8').decode().strip() for l in f]
            for l in lines:
                l = l.strip().lower()
                self.stopwords.append(l)
                if re.match('\w', l):
                    self.stopw_regex.append('(\\b{}\\b)'.format(l))
                else:
                    self.stopw_regex.append('({})'.format(l))

        if self.stopw_regex:
            self.stopw_regex = re.compile('({})'.format('|'.join(self.stopw_regex)))
        else:
            print('[WARNING] No stopword detected!')

    def remove_stopwords_text(self, text):
        if not self.stopw_regex:
            print('[WARNING] No stopword detected!')
            return text
        else:
            res = remove_accents(text.lower())
            res = self.stopw_regex.sub('', res)
            res = re.sub('\s{2,}', ' ', res).strip()
            return res

    def remove_stopwords_corpus(self, corpus):
        if not self.stopw_regex:
            print('[WARNING] No stopword detected!')
        else:
            cleaned = []
            for line in corpus:
                res = self.remove_stopwords_text(line)
                cleaned.append(res)
            return cleaned
