#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import re
import os


sentense = 'Толщина металлического листа 0,6 мм. Тип стали: рулонная, холодной прокатки. Полимерное покрытие: пурал. Толщина защитного слоя, мкм: 50. Текстура покрытия: матовая. Цвет по таблице цветов RAL: RAL3011.'
print (type(sentense))

def sentence_splitter(source,sentenses = []):
  SPLIT = re.compile("(\. )")
  sentenses.extend(re.split(SPLIT, source.decode('utf-8')))
  return [(s if s[-1:] == '.' else s + '.').encode('utf8') for s in sentenses if (s != '. ')]

sentArray = sentence_splitter(sentense)
[print(s) for s in sentArray]

print ('          Hello        '.strip() )