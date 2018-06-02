#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import requests

from flask import Flask, request
from pprint import pprint
from nlu.parsing import NLParser

app = Flask(__name__)
parser = NLParser(intent_data='data/titles.csv')

@app.route('/', methods=['GET'])
def home():
    return 'Quiubo', 200

@app.route('/', methods=['POST'])
def webhook():
    """
    Endpoint for processing incoming messaging events
    """
    global parser
    data = request.get_json()
    pprint(data)

    # parse data
    if 'query' in data.keys():
        if 'k' in data.keys():
            try:
                candidates = parser.cosine_parse(data['query'], int(data['k']))
            except:
                candidates = parser.cosine_parse(data['query'])
        else:
            candidates = parser.cosine_parse(data['query'])
        print(candidates)
        return candidates.to_json(), 200
    else:
        print('[WARNING] found no query!')
        return 'ERROR', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
