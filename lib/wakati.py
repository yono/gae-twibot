#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.parsers.expat import ParserCreate
import yahoowakati
import sys

class Wakati(object):
    def __init__(self):
        self.words = []

    def get_parser(self):
        p = ParserCreate()
        p.buffer_text = True
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        return p

    def start_element(self, name, attrs):
        global flag
        flag = False
        if name == "Surface":
            flag = True

    def end_element(self, name):
        global flag
        flag = False

    def char_data(self, data):
        global flag
        if flag:
            self.words.append(data)

    def parse_text(self, _text):
        text = self._remove_break(_text)
        xml = yahoowakati.get_xml(text)
        parser = self.get_parser()
        parser.ParseFile(xml)

    def get_words(self):
        return self.words

    def _remove_break(self, _text):
        text = _text.replace('\r\n', '')
        text = text.replace('\r', '')
        text = text.replace('\n', '')
        return text


if __name__=="__main__":
    import sys
    text = sys.argv[1]
    w = Wakati()
    w.parse_text(text)
    words = w.get_words()
    for word in words:
        print word
