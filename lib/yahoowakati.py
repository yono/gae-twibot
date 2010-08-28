#!/usr/bin/env python
# -*- coding:utf-8 -*-
import urllib

def get_xml(text):
    url = 'http://jlp.yahooapis.jp/DAService/V1/parse'
    appid = "UzGghtuxg67eFsctoGKO8oFA8mCCTPhCInTKJz7DsgdM4HtUbxTiOz9v_tyne8c-"

    postdata = {
        'appid': appid,
        'sentence': text
    }

    params = urllib.urlencode(postdata)
    result = urllib.urlopen(url, params)
    return result
