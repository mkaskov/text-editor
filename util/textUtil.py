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

afterSpace = ['.', ',',':',')','%']
beforSpace = ['°','(']
emptyStr = ['.','','[newline]']
dotsArr = [".",",","!","?",":",";"]
dotsArrEntity = [".",",","!","?",":",";","(",")"]

pJoinSent = re.compile(u'\.[А-Я]')

def JoinSent(str):
    for match in pJoinSent.finditer(str):
        return str[:match.span()[1]].replace(match.group(),'. '+match.group()[1])+str[match.span()[1]:]

def sent_splitter(source):
  source = decode_from_java(source)
  source = prepare_encode(source.decode('utf-8')+" ")
  source = replace_celsius(source)
  sentences = []

  source = re.sub("[\s\xA0]+", " ", source).strip()
  source = source.replace('[newline]', '\n').replace('[dot]', '')

  while len(re.findall(pJoinSent, source)) > 0:
      source = JoinSent(source)

  source = prepare_encode(source + " ")

  SPLIT = re.compile("\. |\n")
  sentences.extend(re.split(SPLIT, source))
  return [s.encode('utf-8') for s in sentences if s.strip() not in emptyStr]

def replace_celsius(t):
    t = t.encode('utf8')
    t = t.replace(' 0С', ' °С')
    t = t.decode('utf-8')
    return t

def prepare_encode(t):
    return t.replace('\n', '\n[newline]').replace('...', '[threedot]').replace('. ', '[dot]. ')

def prepare_decode(t): return t.replace('[newline]', '').replace('[threedot]', '...').replace('[dot]', '. ')

def decode_from_java(s): return urllib.unquote(s.encode('utf8'))

def printArr(ar): [print(e) for e in ar]

def removeSpaces(t): return re.sub("[\s\xA0]+", " ", t.decode('utf-8')).encode('utf-8').strip()

def buildRetValue(outputs,vocab):
    retValue = StringIO()
    retValue.truncate(0)
    for id,val in enumerate(outputs): retValue.write(getConvertedWord(id,outputs,vocab))
    return retValue.getvalue()

def getConvertedWord(id,outputs,vocab):
    word = vocab[outputs[id]]
    prevWord = None
    nextWord = None
    if id != 0: prevWord = vocab[outputs[id - 1]]
    if id + 1 < len(outputs): nextWord = vocab[outputs[id + 1]]

    # if id==0: word = word.decode('utf8').capitalize().encode('utf8')

    state = getWordState(id,outputs,vocab,word)

    # if not (prevWord is None) and not (nextWord is None): print('state: ', state, ' prev_word: ', prevWord,
    #                                                               ' current_word: ', word, ' next_word: ', nextWord)
    # elif not (prevWord is None): print ('state: ',state,' prev_word: ',prevWord,' current_word: ',word)
    # elif not (nextWord is None): print ('state: ',state,' current_word: ',word,' next_word: ',nextWord)


    for case in switch(state):
        if case('digit'): return word
        if case('beforeSpace'): return ' ' + word
        if case('afterSpace'): return word + ' '
        if case('afterSpaceHasNext'):
            if ')'==word and nextWord.isdigit(): return word + ' '
            elif prevWord is not None and not prevWord.isdigit() and nextWord.isdigit(): return word + ' '
            elif nextWord.isdigit() or '.' == nextWord: return word
            else: return word + ' '
        if case('hasNextWord'):
            if nextWord.isdigit() or '%'==nextWord: return ' ' + word + ' '
            elif nextWord in afterSpace: return ' ' + word
            else: return ' ' + word + ' '
        if case('hasBeforeSpace'):
            if nextWord is not None and nextWord in afterSpace: return word
            else: return word + ' '
        if case(): return ' ' + word + ' '

def getWordState(id,outputs,vocab,word):
    if word.isdigit(): return 'digit'
    elif word in beforSpace: return 'beforeSpace'
    elif word in afterSpace and id + 1 < len(outputs): return 'afterSpaceHasNext'
    elif word in afterSpace: return 'afterSpace'
    elif id != 0 and vocab[outputs[id - 1]] in beforSpace: return 'hasBeforeSpace'
    elif id + 1 < len(outputs): return 'hasNextWord'
    else: return 'default'

def clearDots(tokens):
    retValue = []

    if len(tokens) > 0:
        if not tokens[0] in dotsArr: retValue.append(tokens[0])
        for i in xrange(1, len(tokens) - 1): retValue.append(tokens[i])
        if not tokens[-1] in dotsArr: retValue.append(tokens[-1])

    return " ".join(retValue)

def clearDotsEntity(tokens):
    retValue = []

    if len(tokens) > 0:
        if "(" in tokens and ")" in tokens:
            if not tokens[0] in dotsArr: retValue.append(tokens[0])
        else:
            if not tokens[0] in dotsArrEntity: retValue.append(tokens[0])
        for i in xrange(1, len(tokens) - 1): retValue.append(tokens[i])
        if "(" in tokens and ")" in tokens:
            if not tokens[-1] in dotsArr: retValue.append(tokens[-1])
        else:
            if not tokens[-1] in dotsArrEntity: retValue.append(tokens[-1])

    return " ".join(retValue)