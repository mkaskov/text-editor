#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nnet import data_utils as du
from util import textUtil as tu

import pandas as pd

def connectToBase(url_database,core):
    base = pd.read_excel(url_database, sheetname=0, header=None, names=['category', 'in', 'out'])
    base = base.fillna(value='')

    base['in'] = base['in'].apply(lambda x:  " ".join([x for x in du.tokenizer_tpp(x.encode("utf-8"), core._TTP_WORD_SPLIT) if x not in tu.dotsArrEntity]))
    # base['category'] = base['category'].apply(lambda x: tu.clearDots(du.tokenizer_tpp(x.encode("utf-8"), core._TTP_WORD_SPLIT)))
    base['category'] = base['category'].apply(lambda x:  " ".join([x for x in du.tokenizer_tpp(x.encode("utf-8"), core._TTP_WORD_SPLIT) if x not in tu.dotsArrEntity]))

    return base

def searchInBase(dataBase,category,entity,core):
    finalBase = dataBase

    category = category.strip()

    if len(category) > 0:
        finalBase = dataBase.loc[dataBase['category'] == category]
        if len(finalBase) == 0: finalBase = dataBase

    for index, row in entity.iterrows():
        # searchValue = tu.clearDotsEntity(du.tokenizer_tpp(row["entity"], core._TTP_WORD_SPLIT))
        searchValue = " ".join([x for x in du.tokenizer_tpp(row["entity"], core._TTP_WORD_SPLIT) if x not in tu.dotsArrEntity])
        result = finalBase.loc[finalBase['in'] == searchValue]
        if len(result) > 0: row["answer"] = finalBase.ix[result.iloc[0].name]["out"]

    return entity

def searchCategory(dataBase,category,core):
    # searchValue = tu.clearDots(du.tokenizer_tpp(category, core._TTP_WORD_SPLIT))
    searchValue =  " ".join([x for x in du.tokenizer_tpp(category, core._TTP_WORD_SPLIT) if x not in tu.dotsArrEntity])
    result = dataBase.loc[dataBase['category'] == searchValue]
    return result

def searchInput(dataBase,text,core):
    # searchValue = tu.clearDots(du.tokenizer_tpp(category, core._TTP_WORD_SPLIT))
    searchValue =  " ".join([x for x in du.tokenizer_tpp(text, core._TTP_WORD_SPLIT) if x not in tu.dotsArrEntity])
    result = dataBase.loc[dataBase['in'] == searchValue]
    return result