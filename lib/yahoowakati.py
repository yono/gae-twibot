#!/usr/bin/env python
# -*- coding:utf-8 -*-
import urllib
import os
from ConfigParser import SafeConfigParser

"""
Yahoo API のキーを読み込む
"""
parser = SafeConfigParser()
parser.readfp(open(os.path.join(os.path.dirname(__file__), '../config.ini')))
sec = 'yahoo'
appid = parser.get(sec, 'appid')

def get_xml(text):
    url = 'http://jlp.yahooapis.jp/DAService/V1/parse'

    postdata = {
        'appid': appid,
        'sentence': text
    }

    params = urllib.urlencode(postdata)
    result = urllib.urlopen(url, params)
    return result
