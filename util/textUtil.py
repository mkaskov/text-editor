#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by Max8mk

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import urllib
import re
from .switch import switch
from cStringIO import StringIO

afterSpace = ['.', ',']
beforSpace = ['°']
emptyStr = ['. ','','[newline]']

def sent_splitter(source):
  source = decode_from_java(source)
  source = prepare_encode(source)
  sentences = []
  SPLIT = re.compile("\. |\n")
  sentences.extend(re.split(SPLIT, source))
  return [s for s in sentences if s not in emptyStr]

def prepare_encode(text):
    return text.replace('\n','\n[newline]').replace('...','[threedot]').replace('. ', '[dot]. ')

def prepare_decode(text):
    return text.replace('[newline]', '').replace('[threedot]','...').replace('[dot]', '. ')

def decode_from_java(source):
  return urllib.unquote(source.encode('utf8'))

def printArr(array):
    [print(e) for e in array]

def buildRetValue(outputs,vocab):
    retValue = StringIO()
    retValue.truncate(0)
    for idx,val in enumerate(outputs): retValue.write(getConvertedWord(idx,outputs,vocab))
    return retValue.getvalue()

def getConvertedWord(id,outputs,vocab):
    word = vocab[outputs[id]]
    state = getWordState(id,outputs,vocab,word)
    if id + 1 < len(outputs): nextWord = vocab[outputs[id + 1]]

    for case in switch(state):
        if case('digit'): return word
        if case('beforeSpace'): return ' ' + word
        if case('afterSpace','hasBeforeSpace'): return word + ' '
        if case('afterSpaceHasNext'):
            if id != 0 and not vocab[outputs[id-1]].isdigit() and nextWord.isdigit(): return word + ' '
            if nextWord.isdigit() or '.' == nextWord: return word
            else: return word + ' '
        if case('hasNextWord'):
            if nextWord.isdigit(): return ' ' + word + ' '
            if nextWord in afterSpace: return ' ' + word
            else: return ' ' + word + ' '
        if case(): return ' ' + word + ' '

def getWordState(id,outputs,vocab,word):
    if word.isdigit(): return 'digit'
    elif word in beforSpace: return 'beforeSpace'
    elif word in afterSpace and id + 1 < len(outputs): return 'afterSpaceHasNext'
    elif word in afterSpace: return 'afterSpace'
    elif id != 0 and vocab[outputs[id - 1]] in beforSpace: return 'hasBeforeSpace'
    elif id + 1 < len(outputs): return 'hasNextWord'
    else: return 'default'