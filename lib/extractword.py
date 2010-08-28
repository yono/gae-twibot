#!/usr/bin/env python
# -*- coding:utf-8 -*-
import wakati

class Sentence(object):

    def __init__(self):
        self.words = []
        self.w = wakati.Wakati()

    def get_words(self):
        return self.words

    def analysis_text(self, text):
        self.w.parse_text(text)
        self.words = self.w.get_words()
