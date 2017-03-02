#! /usr/bin/env python
# by Max8mk

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import urllib.parse
import re
from .switch import switch
from io import StringIO

afterSpace = ['.', ',',':',')','%']
beforSpace = ['°','(']
emptyStr = ['.','','[newline]']
dotsArr = [".",",","!","?",":",";","мм","и"]
dotsArrSpace = ["мм","и"]
# dotsArrEntity = [".",",","!","?",":",";","(",")","°","/","\\","-","-","°","и"]
dotsArrEntity = [".",",","!","?",":",";","(",")","/","\\","-","-","и"]

pJoinSent = re.compile(u'\.[А-Я]')

excludeSamples = [
    "или аналог",
    "или эквивалент"
]

ecludeRegexSamples = [
    "тип"
]

def JoinSent(str):
    for match in pJoinSent.finditer(str):
        return str[:match.span()[1]].replace(match.group(),'. '+match.group()[1])+str[match.span()[1]:]

def sent_splitter(source):
  source = decode_from_java(source)
  source = prepare_encode(source+" ")
  source = replace_celsius(source)
  sentences = []

  source = re.sub("[\s\xA0]+", " ", source).strip()
  source = source.replace('[newline]', '\n').replace('[dot]', '')

  while len(re.findall(pJoinSent, source)) > 0:
      source = JoinSent(source)

  source = prepare_encode(source + " ")

  SPLIT = re.compile("\. |\n")
  sentences.extend(re.split(SPLIT, source))
  return [s for s in sentences if s.strip() not in emptyStr]

def replace_celsius(t):
    return t.replace(' 0С', ' °С')

def prepare_encode(t):
    return t.replace('\n', '\n[newline]').replace('...', '[threedot]').replace('. ', '[dot]. ')

def prepare_decode(t): return t.replace('[newline]', '').replace('[threedot]', '...').replace('[dot]', '. ')

def decode_from_java(s): return urllib.parse.unquote(s)

def removeSpaces(t): return re.sub("[\s\xA0]+", " ", t).strip()

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

def getRaw(text, core):
    text = prepareSuperscript(text)
    text =  "".join([x for x in tokenizer_tpp(text, core._TTP_WORD_SPLIT) if x not in dotsArrEntity])
    return prepareCelsius(text)

def getRawSpace(text, core):
    text = prepareSuperscript(text)
    text =  " ".join([x for x in tokenizer_tpp(text, core._TTP_WORD_SPLIT) if x not in dotsArrEntity])
    return prepareCelsius(text)

def getSplitted(text,core):
    return " ".join([x for x in tokenizer_tpp(text, core._TTP_WORD_SPLIT)])

def removeSamples(text,core):
    for sample in excludeSamples:
        sample = getSplitted(sample,core)
        text = re.sub(sample, " ", text)
    for sample in ecludeRegexSamples:
        text = re.sub(sample+"\s(\d\s)+\d+|"+sample+"\s(\d\s)+|"+sample+"\s(\d)+", " ", text)
    return re.sub("[\s]+", " ", text)

def prepareSuperscript(text):
    supSymbols = ['⁰','¹','²','³','⁴','⁵','⁶','⁷','⁸','⁹']
    supWord = ['/м','/мм',"/см","/дм"]
    supWord_v2 = ['м','мм',"см","дм"]

    text = re.sub("\s[0oOоО][СC]", "°C", text)
    text = re.sub("\)\s?[0oOоО][СC]", ") °C", text)

    for i in range(10):
        for word in supWord:
            text = re.sub(word+str(i), word+supSymbols[i], text)
        for word in supWord_v2:
            text = re.sub("\s"+word + str(i), word + supSymbols[i], text)
        text = re.sub(str(i)+"[0oOоО][СC]", str(i)+"°C", text)
        text = re.sub('\*\s?1\s?0\s?-\s?' + str(i), '*10-' + supSymbols[i], text)
    return text

def prepareCelsius(text):
    return re.sub("°[СC]", "°C", text)



# Регулярные выражения, используемые для создания токенов (tokenize).
_WORD_SPLIT = re.compile("([,.][ ]+|[!?\"':;)(])") # v2 (not tested)
_DIGIT_RE = re.compile(r"\d")

_TTP_WORD_SPLIT = None

def basic_tokenizer(sentence): #"""Very basic tokenizer: split the sentence into a list of tokens."""
  words = []
  for space_separated_fragment in sentence.strip().split():
    words.extend(re.split(_WORD_SPLIT, space_separated_fragment))
  return [w for w in words if w]

def tokenizer_tpp(t, _tokens):
  words = re.findall(_tokens, t)
  return [w for w in words if w]