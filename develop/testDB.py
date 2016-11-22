#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from sqlalchemy import create_engine


import pandas as pd
import re
from util import textUtil as tu
from nnet import data_utils as du

# df = pd.read_sql_query('select * from "learnpair"',con=engine)

# print (df)

category = "category"
input = "input"
output = "output"
_TTP_WORD_SPLIT = re.compile(ur"\[_K_\]|\[_At_\]|\[\|\|\]|\[\/K\]|\[K\]|\[At\]|\[\/At\]|гост\s[\d.]+—?\-?[\d]+|ГОСТ\s[\d.]+—?\-?[\d]+|[а-яА-Я]+\/[а-яА-Я\d]+\.{1}[а-яА-Я\d]+\.{1}|[а-яА-Я]+\/\([^()]+\)|[^\s\d.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+\d?\/[^\s.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+|м{1,2}[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|см[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|дм[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|[a-zA-Zа-яА-ЯёЁ]*[^\s\d.\\!?,:;()\"\'<>%«»±^…–—\-*=/+\xA0@·∙\[\]°ₒ”“·≥≤~_\x23]|[\d()\\!?\'\"<>%,:;±«»^…–—\-*=/+@·∙\[\]°ₒ”“·≥≤~_\x23]|\.{3}|\.{1}")

def connectToDB():
    engine = create_engine('postgresql://ttpuser@localhost:5433/ttp')
    base = pd.read_sql_query('select * from "learnpair"', con=engine)
    base['orig'] = base[input]
    base = base.fillna(value='')
    base.drop('id', axis=1, inplace=True)
    base.drop('createddate', axis=1, inplace=True)
    base.drop('userid', axis=1, inplace=True)

    base[input] = base[input].apply(lambda x: getRaw(x.encode("utf-8")))
    base['orig'] = base['orig'].apply(lambda x: re.sub("[\s]+", " ", x.encode("utf-8")))
    base[category] = base[category].apply(lambda x: getRaw(x.encode("utf-8")))
    return base

def getRaw(text):
    return "".join([x for x in du.tokenizer_tpp(text, _TTP_WORD_SPLIT) if x not in tu.dotsArrEntity])

base = connectToDB()
maxLenChar = base[input].map(lambda x: len(x.decode("utf-8"))).max()

print (base)
print (maxLenChar)
