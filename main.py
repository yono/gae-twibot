#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue

import random
import re
import sys
from ConfigParser import SafeConfigParser

import twoauth

### 文字コード設定 ###
stdin = sys.stdin
stdout = sys.stdout
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin = stdin
sys.stdout = stdout
######################

"""
OAuth の各種キーを読み込む
"""
parser = SafeConfigParser()
parser.readfp(open('config.ini'))
sec = 'oauth'
consumer_key = parser.get(sec, 'consumer_key')
consumer_secret = parser.get(sec, 'consumer_secret')
access_token = parser.get(sec, 'access_token')
access_token_secret = parser.get(sec, 'access_token_secret')

sec = 'bot'
tweet_type = int(parser.get(sec, 'tweet_type'))
reply = parser.get(sec, 'reply')
auto_refollow = parser.get(sec, 'auto_refollow')

api = twoauth.api(consumer_key,
                  consumer_secret,
                  access_token,
                  access_token_secret)

"""
sentence.txt を読み込む
"""
sentences = []

class Since(db.Model):
    id = db.IntegerProperty()

class PostTweetHandler(webapp.RequestHandler):
    def get(self):
        tweet = get_tweet(False)
        api.status_update(tweet)

class ReplyTweetHandler(webapp.RequestHandler):
    def get_sinceid(self):
        since_id = memcache.get('since_id')
        if since_id is None:
            since = Since.get_by_key_name('since_id')
            if since is not None:
                since_id = since.id
        return since_id
    
    def set_sinceid(self, since_id):
        memcache.set('since_id', since_id)
        Since(key_name='since_id', id=int(since_id)).put()
        
    def get(self):
        mentions = api.mentions(since_id=self.get_sinceid())

        reply_start = re.compile(u'(@.+?)\s', re.I | re.U)

        last_tweet = ''

        for status in mentions:
            screen_name = status['user']['screen_name']

            tweet = get_tweet(True)
            while tweet == last_tweet:
                tweet = get_tweet(True)
            last_tweet = tweet
            tweet = "@%s %s" %(screen_name, tweet)

            last_since_id = status['id']
            self.set_sinceid(last_since_id)
            api.status_update(tweet, in_reply_to_status_id=last_since_id)
            

class SinceIdHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(str(memcache.get('since_id')))


"""
ツイート内容を決める

マルコフ連鎖を使う場合
=====
return tweet_from_db()
=====

ファイルに書かれてる文章をランダムにつぶやく
file: sentence.txt
=====
return tweet_randomly_from_text('sentence.txt')
=====
"""

def get_tweet(reply):
    if reply == True:
        if tweet_type == 1:
            return tweet_from_db()
        elif tweet_type == 2:
            return tweet_randomly_from_text('sentence.txt')
    elif reply == False:
        if tweet_type == 1:
            return tweet_from_db() 
        elif tweet_type == 2:
            tweet = tweet_randomly_from_text('sentence.txt')
            return tweet

def tweet_randomly_from_text(text):
    if sentences == []:
        sentence = []
        for line in open(text).read().splitlines():
            if line.startswith('%'):
                if sentence != []:
                    sentences.append('\n'.join(sentence))
                    sentence = []
            else:
                sentence.append(line)
        if sentence != []:
            sentences.append('\n'.join(sentence))
    return random.choice(sentences)


def main():
    application = webapp.WSGIApplication(
            [('/tweet', PostTweetHandler),
            ('/reply', ReplyTweetHandler),
            ('/since_id', SinceIdHandler),
            ],
    debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
    
