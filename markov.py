#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.api.labs import taskqueue
from google.appengine.api import urlfetch, memcache

import datetime
import re
import sys
import twilog

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from markovchains import MarkovChain

"""
OAuth の各種キーを読み込む
"""
parser = SafeConfigParser()
parser.readfp(open('config.ini'))
sec = 'twilog'
original_id = parser.get(sec, 'original_id')

### 文字コード設定 ###
stdin = sys.stdin
stdout = sys.stdout
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin = stdin
sys.stdout = stdout
######################


def parse_tweet(text):
    reply = re.compile(u'@[\S]+')
    url = re.compile(r's?https?://[-_.!~*\'()a-zA-Z0-9;/?:@&=+$,%#]+', re.I)

    text = reply.sub('', text)
    text = url.sub('', text)
    text = text.replace(u'．', u'。')
    text = text.replace(u'，', u'、')
    text = text.replace(u'「', '')
    text = text.replace(u'」', '')
    text = text.replace(u'？', u'?')
    text = text.replace(u'！', u'!')
    return text

"""
POST された文章を元に新しい文章生成
"""
def get_sentence(sentence):
    m = MarkovChains()
    m.analyze_sentence(sentence)
    return m.make_sentence()

"""
GET:  DB を元に生成した新しい文章を返す
POST: 投げられた文章を解析して DB に突っ込む
"""

def get_sentence_from_db():
    m = MarkovChains()
    m.load_db('gquery2')
    taskqueue.add(url='/task/talk')
    return m.db.fetch_new_sentence()

def analyse_sentence_to_db(sentence):
    taskqueue.add(url='/task/learn',
            params={'sentences': sentence})

"""
文章を生成してキューに貯める
"""
class ApiDbSentenceTalkTask(webapp.RequestHandler):
    def post(self):
        m = MarkovChains()
        m.load_db('gquery2')
        m.db.store_new_sentence()

"""
文章を解析して DB に保存
"""
class ApiDbSentenceLearnTask(webapp.RequestHandler):
    def post(self):
        text = self.request.get('sentences')
        m = MarkovChains()
        m.load_db('gquery2')
        m.db.store_sentence(text)

"""
memcache の中身を全削除
"""
class DeleteHandler(webapp.RequestHandler):
    def get(self):
        memcache.flush_all()

"""
Twilog から学習
"""
class LearnTweetHandler(webapp.RequestHandler):
    def get(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        log = twilog.Twilog()
        tweets = log.get_tweets(original_id, yesterday)
        for tweet in tweets:
            text = parse_tweet(tweet)
            sentences = text.split(u'。')
            for sentence in sentences:
                analyse_sentence_to_db(sentence)
