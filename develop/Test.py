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

# arr = [0,1,2,3]
#
# [print (x) for x in arr]
#
# print (arr[0])
# print (arr[-1])
#
# # arrayStr = ",".join(str(x) for x in arr)
#
# arrayStr = ', '.join(map(str, arr))
from datetime import datetime


from elasticsearch import Elasticsearch

# if __name__ == '__main__':
#     es = Elasticsearch()
#     res = es.search(index="test", doc_type="articles", body={"query": {"match": {"content": "fox"}}})
#     print("%d documents found:" % res['hits']['total'])
#     for doc in res['hits']['hits']:
#         print("%s) %s" % (doc['_id'], doc['_source']['content']))

# """
# Simple example of querying Elasticsearch creating REST requests
# """
# import requests
# import json
#
#
# def search(uri, term):
#     """Simple Elasticsearch Query"""
#     query = json.dumps({
#         "query": {
#             "match": {
#                 "content": term
#             }
#         }
#     })
#     response = requests.get(uri, data=query)
#     results = json.loads(response.text)
#     return results
#
#
# def format_results(results):
#     """Print results nicely:
#     doc_id) content
#     """
#     data = [doc for doc in results['hits']['hits']]
#     for doc in data:
#         print("%s) %s" % (doc['_id'], doc['_source']['content']))
#
#
# def create_doc(uri, doc_data={}):
#     """Create new document."""
#     query = json.dumps(doc_data)
#     response = requests.post(uri, data=query)
#     print(response)
#
#
# if __name__ == '__main__':
#     uri_search = 'http://localhost:9200/test/articles/_search'
#     uri_create = 'http://localhost:9200/test/articles/'
#
#     # create_doc(uri_create, {"content": "The fox 2  rwetw!"})
#     results = search(uri_search, "fox 2")
#     format_results(results)
#
#
#     # results = search(uri_search, "fox")
#     # format_results(results)

# app_options = {"usegpu":False,"fixdataset":False}
#
#
#
# print (app_options)
# # for opt in app_options:
# #     print (opt)
# #     print (len(opt))
# #     print (app_options[opt])
#
#
# for id, arg in enumerate(sys.argv[1:]):
#     # print (id,arg)
#     for opt in app_options:
#         if opt in arg:app_options[opt]=True if arg[len(opt)+3:]=='true' else False
#
# print(app_options)
#
#
# app_options["sdfsdf"] = False

    # if '--data_dir' in arg: data_dir = sys.argv[1:][id + 1]
    # if '--usegpu' in arg:
    #     useGPU = True if sys.argv[1:][id][9:] == 'true' else False
    # if '--fixdataset' in arg:
    #     fixDataSet = True if sys.argv[1:][id][13:] == 'true' else False

# str = "[cellid]2[/cellid]\n[||]Рейки деревянные 8х18 мм\n\n[||]Допускаются трещины длиной до 100% ширины пиломатериала расположенные на торце за исключением вызванными усушкой. Допускается изменение строения древесины в сжатой зоне ствола и сучьев, проявляющееся в виде кажущегося резкого утолщения поздней древесины годичных слоев размером до 66,6 % площади пласти материала. Допускается до 1/2 длины пиломатериала углубление или вздутие, возникающее на поверхности растущего дерева в результате деятельности грибов или бактерий. Допускается на периферию) бурого, красноватого, серого и серо-фиолетового цвета; на продольных разрезах - в виде вытянутых пятен и полос тех же цветов. Допускаются общей площадью до 66,6 % от площади пиломатериала грибница и плодоношения плесневых грибов на поверхности древесины, в виде отдельных пятен или сплошного налета, ненормально окрашенные участки заболони без понижения твердости древесины, возникающие в срубленной древесине под воздействием деревоокрашивающих грибов, не вызывающих образования гнили; которые распространяются вглубь древесины от торцов и боковых поверхностей, на торцах в виде пятен разной величины и формы или сплошного поражения заболони, на боковых поверхностях - в виде вытянутых пятен, полос или сплошного поражения заболони. Не допускается ненормальные по цвету участки древесины с понижением твердости, возникающие под воздействием дереворазрушающих грибов. Качество не клееных лесоматериалах изготовленных из сосны или ели или пихты должно быть до IV сорта. Не параллельность пластей и кромок должна допускаться в пределах отклонений от номинальных размеров.\n\n[||] "
#
# indexLast = str.find('[/cellid]')
#
# print (indexLast)
#
# cellIdIndex = indexLast+len("[/cellid]")
# # print ("----------------------------------------")
# # print (str[cellIdIndex:])
# # print ("----------------------------------------")
# # print (str[:cellIdIndex])
#
# cellText = str[:cellIdIndex]
#
# cellInd = str[len("[cellid]"):str.find('[/cellid]')]
#
# print (int(cellInd))

# str = "Дверь  однопольная, размером не менее 900х не более 2100 мм"
#
# pos = str.find("металлическая")
#
# print (pos)

# from PIL import Image
# img = Image.open("/home/user/Pictures/apple.jpg")
# img2 = img.rotate(90,expand=True)
# img2.save("/home/user/Pictures/apple90.jpg")

total = 100
current = 0
for i in range(total):
    current +=1
    print (current,current%total)
    # if i%total == 0: print (i)

