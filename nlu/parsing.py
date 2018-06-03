#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

VECTORIZER = TfidfVectorizer(analyzer='word',
                             ngram_range=(1, 5))
NONE_VAL = ''
NON_WORDS = re.compile('[^\w\s]')

class NLParser:
    """Wrapper class for all parsing algorithms.
    """

    def __init__(self, intent_data, entity_data=None):
        """Intents and entities are encouraged to be provided
        in order to save memory in further computations.
        """
        if isinstance(intent_data, list):
            self.intents = pd.DataFrame(intent_data)
            self.intents = self.intents.set_index('id')
        else:
            self.intents = pd.read_csv(intent_data,
                                       index_col='id',
                                       encoding='utf-8')
        self.intents = self.intents.fillna(value=NONE_VAL)
        self._clean_intents()


    def _clean_intents(self):
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')
        print('Augmenting intent internal representation...')

        # downcase words
        self.intents.title = self.intents.title.apply(lambda row: row.lower())
        self.intents.description = self.intents.description.apply(lambda row: row.lower())

        # further cleaning
        self.intents.title = self.intents.title.apply(lambda row: NON_WORDS.sub('', row))
        self.intents.description = self.intents.description.apply(lambda row: NON_WORDS.sub('', row))
        self.intents['train'] = self.intents.title + ' ' + self.intents.description

        print('DONE')


    def _slice_intents(self, key):
        """Returns a pandas DataFrame according to the given intent key (or list of keys).
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')

        if isinstance(key, str):
            if key not in self.intents.index.values:
                raise KeyError('[ERROR] Given key ({}) is not defined in intent DataFrame'.format(key))
            else:
                return self.intents[self.intents.index == key]
        else:
            sliced = pd.DataFrame()
            for k in key:
                if k not in self.intents.index.values:
                    raise KeyError('[ERROR] Given key ({}) is not defined in intent DataFrame'.format(k))
                else:
                    sliced = sliced.append(self.intents[self.intents.index == k])
            return sliced

    def cosine_single_comparison(self, query, intent):
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')
        try:
            assert intent in self.intents.index
        except:
            raise Exception('[ERROR] ({}) not defined in intent list'.format(intent))

        key = self._slice_intents([intent]).DOC.values[0]
        tfidfs = VECTORIZER.fit_transform([key, query])
        return cosine_similarity(tfidfs[0, :], tfidfs[1, :]).squeeze()

    def cosine_parse(self, query, k=5, data=None, **kwargs):
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')

        # add query to intent frame
        if data is None:
            query_frame = self.intents.copy()
        else:
            query_frame = data.copy()
        cleaned = query.lower()
        new_row = pd.DataFrame({'title': '',
                                'description': '',
                                'train': cleaned},
                               index=['TBD'])
        query_frame = query_frame.append(new_row)

        # compute TF-IDF scores
        tfidfs = VECTORIZER.fit_transform(query_frame.train)

        # compute cosine similarity scores
        query_tfidf = tfidfs[-1, :]
        comps = []
        for i, vect in enumerate(tfidfs[:-1, :]):
            score = cosine_similarity(query_tfidf, vect).squeeze()
            comps.append(score)
        comps = pd.DataFrame(index=query_frame.index[:-1],
                             data={'SCORE': comps})
        comps.SCORE = comps.SCORE/sum(comps.SCORE)
        comps.SCORE = comps.SCORE.astype(float)
        if kwargs is not None:
            if 'serialize' in kwargs and kwargs['serialize']:
                ax = comps.astype(float).plot(kind='bar')
                fig = ax.get_figure()
                fig.tight_layout()
                fig.savefig('scores.png')
                return comps.nlargest(k, 'SCORE')
            else:
                return comps.nlargest(k, 'SCORE')
        else:
            return comps.nlargest(k, 'SCORE')

    def regex_parse(self, text, regex):
        return [match.group() for match in regex.finditer(text)]

    def intent_parse(self, query, intents, verbose=False, **kwargs):
        """
        Main intent parsing pipeline.
        If the given (cleaned) query has at most 3 words,
        a regex match is performed, before the cosine matching.
        """
        try:
            assert hasattr(self, 'intents')
        except:
            raise Exception('[ERROR] Intent list not defined!')

        # check if list of intents is valid
        try:
            assert intents
        except:
            raise Exception('[ERROR] Intent list must be nonempty!')
        for intent in intents:
            if intent not in self.intents.index:
                raise Exception('[ERROR] Intent {} not defined in parser object!'.format(intent))

        # build verbose function
        if verbose:
            verb = lambda s: print(s)
        else:
            verb = lambda _: None

        # slice the corresponding intent rows
        arcs = self._slice_intents(intents)

        # preprocess query
        text = remove_accents(query.lower())
        text = re.sub('[^\w\s]', ' ', text).split()
        text = ' '.join(text)

        if len(query.split()) <= 3:
            # perform a regex search
            verb('Attempting regex parse...')
            matches = [index
                       for index, regex
                       in arcs.REGEX.iteritems()
                       if self.regex_parse(text, regex)]
            if len(matches) == 1:
                verb('Regex parse successful!!')
                return matches[0], 1.0
            else:
                verb('Regex parse not successful!!')
                verb('Attempting cosine parse...')
                return self.cosine_parse(text, data=arcs, **kwargs)
        else:
            verb('Attempting cosine parse...')
            return self.cosine_parse(text, data=arcs, **kwargs)
