#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import re
import string
import sys
import logging

from slugify import Slugify, UniqueSlugify, slugify, slugify_unicode
from slugify import slugify_url, slugify_filename
from slugify import slugify_ru, slugify_de

# sentense = 'Толщина металлического листа 0,6 мм. Тип стали: рулонная, холодной прокатки. Полимерное покрытие: пурал. Толщина защитного слоя, мкм: 50. Текстура покрытия: матовая. Цвет по таблице цветов RAL: RAL3011.'
# print (type(sentense))
#
# def sentence_splitter(source,sentenses = []):
#   SPLIT = re.compile("(\. )")
#   sentenses.extend(re.split(SPLIT, source.decode('utf-8')))
#   return [(s if s[-1:] == '.' else s + '.').encode('utf8') for s in sentenses if (s != '. ')]
#
# sentArray = sentence_splitter(sentense)
# [print(s) for s in sentArray]
#
# print ('          Hello        '.strip() )
#
# print (('аываы'.strip().capitalize()))
#
# zzz = 'аываы FSDF'.decode('utf-8').capitalize()
#
# print (zzz)
#
#
# # slugify = Slugify(translate=None,capitalize=True, separator=' ')
#
# # print (slugify(' ываываыв'))  # 'any-text')
#
# s = "sdfs sdfsd     sdfsfd"
# s = re.sub("[\s]+", " ", s).strip()
#
# print (s)
#
# s = " Габаритные размеры :   110 х 140 х 35 мм.".decode('utf-8')
# s = re.sub("[\s\xA0]+", " ", s).strip()
# # s = re.sub("[\s]+", " ", s).strip()
#
# print (s)
# #
# # s = " Габаритные размеры :   110 х 140 х 35 мм."
# # s = re.sub('[\s]+','', s.rstrip())
# # print (s)
#
#
#
# print ('Number of arguments:', len(sys.argv), 'arguments.')
# print ('Argument List:', str(sys.argv))
#
# s = "[li]поперечных >81 (8,1) до 133 (13,3)"
# s = s[4:]
#
# print (s)

# sentence = '38 Клей плиточный <Юнис Гранит> или эквивалент с характеристиками: Температура проведения работ От +5 °C до +30 °C. Пропорции смешивания 1 часть воды на 4,4—5,5 части сухой смеси. Оптимальная толщина слоя 3—10 мм. Расход при нанесении гребёнкой 6х6 мм 3,5 кг/м². Минимальное время жизни раствора 180 минут. Рабочее время (после нанесения на поверхность) 15 минут. Время корректировки плитки 10 минут. Время до пешего хождения 24 часа. Адгезия с основанием 15 кг/см² (1,5 МПа). Удерживаемый вес 100 кг/м². Морозостойкость Более 35 циклов. Температура эксплуатации От -50 до +50 мВт/м·К'
# sentence = re.sub("[\s\xA0]+", " ", sentence.decode('utf-8')).strip()
# _TTP_WORD_SPLIT = re.compile(ur"ГОСТ\s[\d]+\-?[\d]+|[а-яА-Я]+\/[а-яА-Я\d]+\.{1}[а-яА-Я\d]+\.{1}|[а-яА-Я]+\/\([^()]+\)|[^\s\d.,():]+\d?\/[^\s.,():]+|м{1,2}[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|см[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|дм[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|[a-zA-Zа-яА-ЯёЁ]*[^\s\d.!?,:;()\"\'<>%«»±^…\-*=/\xA0]|[\d()!?\'\"<>%,:;±«»^…\-*=/]|\.{3}|\.{1}")
#
# words = re.findall(_TTP_WORD_SPLIT, sentence)
# [print(w.encode('utf-8')) for w in words if w]
# print ('-----------------------------')

# test = 'ГОСТ      28013-98'
# print (test)
# test = re.sub("[\s\xA0]+", " ", test)
# print (test)
#
# bucketsText = '[(5, 5);(10, 10);(30, 30);(50, 50);(70, 70);(110,110)]'
# bucketsText = bucketsText.split(';')
#
# _buckets = []
# for elem in bucketsText :
#     nums = re.findall('\d+', elem)
#     _buckets.append((int(nums[0]),int(nums[1])))
#
# print (_buckets)


# import sys
#
# class Logger(object):
#     def __init__(self,filename):
#         filename+="logfile.log"
#         self.terminal = sys.stdout
#         self.log = open(filename, "a")
#
#     def write(self, message):
#         self.terminal.write(message)
#         self.log.write(message.encode('utf-8'))
#
#     def flush(self):
#         #this flush method is needed for python 3 compatibility.
#         #this handles the flush command by doing nothing.
#         #you might want to specify some extra behavior here.
#         pass
#
# sys.stdout = Logger()

# logging.debug('debug')
# logging.info('info')
# logging.warning('warning')
# logging.error('error')
# logging.exception('exp')

# string = "sdfsdf sdfsd 22222222 sdgdfgd машина"
# print (type(string))
# string= string.decode('utf-8')
# params =ur'[a-zA-Zа-яА-ЯёЁ]*[^\s\d.\\!?,:;()\"\'<>%«»±^…–\-*=/+\xA0@·∙\[\]°ₒ”“·≥≤~_]'
#
# # this_word_split= re.compile(ur'{}'.format(params))
# this_word_split= re.compile(params)
# words = re.findall(this_word_split, string)
#
# [print(x) for x in words]
#
#
# print (type(string))
#
# string= string.encode('utf-8')
# print (type(string))
#
# for x in xrange(1000):
#     print ('--------------------')
#     print (x+1)
#     print ((x+1)%1000)
#     if (x+1)%1000 == 0: print((x+1)/10)

# if errosNum % linesNum == 0: print ("Processing:",errosNum/linesNum,"%")

# string1 = "Машина "
# string2 = "Машина"
#
# print (re.sub("[\s\xA0]+", "", string1) == re.sub("[\s\xA0]+", "", string2))
#
# str = 'I love %(1)s and %(2)s, he loves %(1)s and %(2)s.' % {"1" : "apple", "2" : "pitch"}
# print (str)

# s = "машина ехала по обочине"
#
# print (s.title())

# import nltk
# sent = "Albert Einstein spent many years at Princeton University in New Jersey"
# sent1 = nltk.word_tokenize(sent)
# sent2 = nltk.pos_tag(sent1)
# sent3 = nltk.ne_chunk(sent2)
# print (sent3)


# _TTP_WORD_SPLIT = re.compile(ur"\[\/K\]|\[K\]|\[At\]|\[\/At\]|гост\s[\d.]+—?\-?[\d]+|ГОСТ\s[\d.]+—?\-?[\d]+|[а-яА-Я]+\/[а-яА-Я\d]+\.{1}[а-яА-Я\d]+\.{1}|[а-яА-Я]+\/\([^()]+\)|[^\s\d.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+\d?\/[^\s.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+|м{1,2}[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|см[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|дм[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|[a-zA-Zа-яА-ЯёЁ]*[^\s\d.\\!?,:;()\"\'<>%«»±^…–—\-*=/+\xA0@·∙\[\]°ₒ”“·≥≤~_\x23]|[\d()\\!?\'\"<>%,:;±«»^…–—\-*=/+@·∙\[\]°ₒ”“·≥≤~_\x23]|\.{3}|\.{1}") #v4
#
# # подсчет количества слов в предложении
# def tokenizer_tpp(sentence):
#     #sentence = sentence.decode('utf-8')
#     words = []
#     try:
#         words = re.findall(_TTP_WORD_SPLIT, sentence)
#     except TypeError:
#         print ('TypeError: ',sentence)
#     return len(words)
#
# s = ur"asdasd asdasdas asdasdas, asdasd 123.."
# print (tokenizer_tpp(s))

import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
#     level=logging.INFO)
#
# print ('sdfsdfs')

arr = [0,1,2,3]

[print (x) for x in arr]

print (arr[0])
print (arr[-1])

# arrayStr = ",".join(str(x) for x in arr)

arrayStr = ', '.join(map(str, arr))