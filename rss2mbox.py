#!/usr/bin/env python
#
# rss2mbox reads urls to RSS-feeds from stdin, fetch them and prints
# each article as an htmlized mail in a mbox format to
# stdout. HTML-rendering is delegated to the MUA.
#
# Written using Python 2.6.1 and require feedparser.
#
# Copyright (c) 2009 Sebastian A. Liem <sebastian at liem dot se>
#
# Permission to use, copy, modify, and distribute this work for any
# purpose with or without fee is hereby granted.
#


from time import strftime, gmtime
from email.header import Header
from email.mime.text import MIMEText
from hashlib import md5
import feedparser, cPickle, sys, mailbox, os

hashdbpath = os.getenv("HOME") + "/.rsshashes"

def entry2msg(e, title, encoding):

    body = '<head><meta http-equiv="Content-Type" content="text/html; charset=' + encoding + '"></head>\n'

    body += e.get('id', '') + '<br>\n' 
    body += e.get('summary', '') + '<br>\n'

    for i in e.get('content', []):
        body += i.value + '<br>\n'

    m = MIMEText(body.encode(encoding, 'replace'), 'html', encoding)

    m['From'] = Header(title, encoding)
    m['Subject'] = Header(e.get('title', 'No title'), encoding)
    m['Date'] = strftime('%a, %d %b %Y %H:%M:%S +0000',
                         e.get('published_parsed', gmtime()))

    return mailbox.mboxMessage(m)

def createhashdb():
    db = []
    f = open(hashdbpath, 'wb')
    cPickle.dump(db, f, 2)
    f.close()

def gethashdb():
    try:
        f = open(hashdbpath, 'rb')
    except IOError:
        createhashdb()
        f = open(hashdbpath, 'rb')

    hashdb = cPickle.load(f) 
    f.close()

    return hashdb

def savehashdb(db):
    f = open(hashdbpath, "wb")
    cPickle.dump(db, f, 2)
    f.close()


def hashentry(e):
    h = md5()

    if e.has_key('title'): h.update(e.title.encode('utf-8'))
    if e.has_key('summary'): h.update(e.summary.encode('utf-8'))

    for i in e.get('content', []):
        h.update(i.value.encode('utf-8'))

    return h.hexdigest()

def main():
    hashdb = gethashdb()

    for url in sys.stdin.xreadlines():
        f = feedparser.parse(url)

        for entry in f.entries:

            # Check if we already delivered the article.
            hash = hashentry(entry)
            if hash in hashdb:
                continue
            hashdb.append(hash)

            print(entry2msg(entry, f.feed.get('title', ''), f.get('encoding', 'utf-8')))

    savehashdb(hashdb)

    exit(0);

if __name__ == '__main__':
    main()
