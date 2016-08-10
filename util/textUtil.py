#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by Max8mk

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import urllib
import re

def sent_splitter(source):
  source = decode_from_java(source)
  source = prepare_encode(source)
  sentences = []
  SPLIT = re.compile("\. |\n")
  sentences.extend(re.split(SPLIT, source))
  return [s.encode('utf8') for s in sentences if s != '. ' and s !='' and s!='[newline]']

def prepare_encode(text):
    return text.replace('\n','\n[newline]').replace('...','[threedot]').replace('. ', '[dot]. ')

def prepare_decode(text):
    return text.replace('[newline]', '').replace('[threedot]','...').replace('[dot]', '. ')

def decode_from_java(source):
  return urllib.unquote(source.encode('utf8')).decode('utf-8')

def printArr(array):
    [print(e) for e in array]