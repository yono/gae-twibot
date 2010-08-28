#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
from HTMLParser import HTMLParser
import time
import urllib2
import urlparse


class Twilog(object):

    BASEURL = "http://twilog.org/"

    def __init__(self):
        self.parser = TwilogParser()

    def get_html(self, url):
        time.sleep(5)
        fp = urllib2.urlopen(url)
        html = unicode(fp.read(), 'utf-8', 'ignore')
        return html

    def get_url(self, user, aday=''):
        url = self.BASEURL + user
        if aday:
            return url + '/date-' + self.get_url_date(aday)
        else:
            return url

    def get_tweets(self, user, start='', end=''):
        results = []
        if start == end == '':
            results = self.get_tweets_from_web(user)
        elif start == '' and end:
            results = self.get_tweets_from_web(user, end)
        elif start and end == '':
            results = self.get_tweets_from_web(user, start)
        else:
            from_date, to_date = start, end
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            current_date = from_date
            while current_date <= to_date:
                results.extend(self.get_tweets_from_web(user, current_date))
                current_date += datetime.timedelta(days=1)

        return results

    def get_tweets_from_web(self, user, aday=''):
        url = self.get_url(user, aday)
        html = self.get_html(url)
        self.parser.sentences = []
        self.parser.feed(html)
        tweets = self.parser.sentences
        return tweets

    def get_url_date(self, aday):
        year = str(aday.year)[2:4]
        month = self.format_date(str(aday.month))
        day = self.format_date(str(aday.day))
        return "%s%s%s" % (year, month, day)

    def format_date(self, date):
        return date if len(date) == 2 else "0%s" % (date)


class TwilogParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.flag = False
        self.words = []
        self.sentences = []

    def handle_starttag(self, tag, attrs):
        attrs_dic = dict(attrs)

        if tag == 'p' and 'class' in attrs_dic:
            if attrs_dic['class'] == 'tl-text':
                self.flag = True

    def handle_data(self, data):
        if self.flag:
            self.words.append(data)

    def handle_endtag(self, tag):
        if tag == 'p':
            sentence = ''.join(self.words)
            if sentence != '':
                self.sentences.append(sentence)
            self.words = []
            self.flag = False

if __name__ == '__main__':
    log = Twilog()
    tweets = log.get_tweets('yono')
    for tweet in tweets:
        print tweet

    print '------ Today\'s Tweets ------'

    tweets = log.get_tweets('yono', datetime.date.today(),
                            datetime.date.today())
    for tweet in tweets:
        print tweet
