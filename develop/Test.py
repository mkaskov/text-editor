#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import re
import string
import sys

from slugify import Slugify, UniqueSlugify, slugify, slugify_unicode
from slugify import slugify_url, slugify_filename
from slugify import slugify_ru, slugify_de

sentense = 'Толщина металлического листа 0,6 мм. Тип стали: рулонная, холодной прокатки. Полимерное покрытие: пурал. Толщина защитного слоя, мкм: 50. Текстура покрытия: матовая. Цвет по таблице цветов RAL: RAL3011.'
print (type(sentense))

def sentence_splitter(source,sentenses = []):
  SPLIT = re.compile("(\. )")
  sentenses.extend(re.split(SPLIT, source.decode('utf-8')))
  return [(s if s[-1:] == '.' else s + '.').encode('utf8') for s in sentenses if (s != '. ')]

sentArray = sentence_splitter(sentense)
[print(s) for s in sentArray]

print ('          Hello        '.strip() )

print (('аываы'.strip().capitalize()))

zzz = 'аываы FSDF'.decode('utf-8').capitalize()

print (zzz)


# slugify = Slugify(translate=None,capitalize=True, separator=' ')

# print (slugify(' ываываыв'))  # 'any-text')

s = "sdfs sdfsd     sdfsfd"
s = re.sub("[\s]+", " ", s).strip()

print (s)

s = " Габаритные размеры :   110 х 140 х 35 мм.".decode('utf-8')
s = re.sub("[\s\xA0]+", " ", s).strip()
# s = re.sub("[\s]+", " ", s).strip()

print (s)
#
# s = " Габаритные размеры :   110 х 140 х 35 мм."
# s = re.sub('[\s]+','', s.rstrip())
# print (s)



print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))

