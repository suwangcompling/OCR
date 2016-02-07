## OCR

from PIL import Image
import pytesseract
file = pytesseract.image_to_string(Image.open('test01.JPG'))

## SPELLING CHECKER I (Norvig-Spelling-Corrector)

# Training

# read training data from 'http://norvig.com/big.txt'
import urllib2, cookielib
site = 'http://norvig.com/big.txt'
hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
req = urllib2.Request(site, headers=hdr)
try:
    f = urllib2.urlopen(req)
except urllib2.HTTPError, e:
    print e.fp.read()
tr = f.read()
f.close()

# training (code: 'https://github.com/mattalcock/blog/blob/master/2012/12/5/python-spell-checker.rst')
import re, collections

def words(text):
    return re.findall('[a-z]+', text.lower())

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

NWORDS = train(words(tr))
alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
    s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in s if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in s for c in alphabet if b]
    inserts    = [a + c + b for a, b in s for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words):
    return set(w for w in words if w in NWORDS)

def correct(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    return max(candidates, key=NWORDS.get)

## SPELLING CHECKER II (autocorrect)

from autocorrect import spell
''' Usage
    >>> spell('acress')
    'across'
'''

## PERFORMANCE TESTS

import time
def timer(func, arg):
    start = time.time()
    func(arg)
    end = time.time()
    return end - start

# for correct()
timer(correct,'acress') # 0.000185966491699
# for spell()
timer(spell,'acress') # 0.189234972
# for ocr ensemble
timer(ocr,'test01.JPG') # 23.244197130203247

## CLEAN-UP

import nltk
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')

def cleanup(text): # arg: file from OCR (i.e. file = pytesseract.image_to_string(Image.open('test01.JPG')))
    text = text.decode('utf-8') # get ride of e.g. x082
    text = tokenizer.tokenize(text) # strip punctuations
    text = [w.encode('ascii','ignore') for w in text] # get ride of \utfxxx encoding
    text = [w for w in text if not w.startswith('_')]
    return text

## ONE-STOP ENSEMBLE

# OCR utilities
from PIL import Image
import pytesseract
# spelling correction utilities
import re, collections
# text cleanup utilities
import nltk
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')

''' OCR
    args:
        image (jpg,jpeg,png)
    return:
        list of strings/words
'''
def ocr(image):
    text = pytesseract.image_to_string(Image.open(image))
    text = text.decode('utf-8') # get rid of e.g. x082
    text = tokenizer.tokenize(text) # strip punctuations
    text = [w.encode('ascii','ignore') for w in text] # get rid of \utfxxx encoding
    text = [w for w in text if not w.startswith('_')] # get rid of underscores
    text = [w.lower() for w in text] # lowering case
    text = [correct(w) for w in text] # spelling correction
    return text




