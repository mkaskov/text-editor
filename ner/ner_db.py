#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nnet import data_utils
from util import textUtil

import pandas as pd

def connectToBase(url_database,core):
    textbase = pd.read_excel(url_database, header=None, names=['category', 'in', 'out'])
    textbase = textbase.fillna(value=' ')
    pd.isnull(textbase).any(1).nonzero()[0]  # проверка nan значений

    textbase['in'] = textbase['in'].apply(lambda x: textUtil.clearFromDots(data_utils.tokenizer_tpp(x.encode("utf-8"),core._TTP_WORD_SPLIT)))
    textbase['category'] = textbase['category'].apply(lambda x: textUtil.clearFromDots(data_utils.tokenizer_tpp(x.encode("utf-8"),core._TTP_WORD_SPLIT)))

    return textbase

def searchInBase(dataBase,category,entity,core):
    if len(category) > 0:
        finalBase = dataBase.loc[dataBase['category'] == category]
        if len(finalBase) == 0: finalBase = dataBase
    else:
        finalBase = dataBase

    for index, row in entity.iterrows():
        searchValue = textUtil.clearFromDots(data_utils.tokenizer_tpp(row["entity"],core._TTP_WORD_SPLIT))
        result = finalBase.loc[finalBase['in'] == searchValue]
        if len(result) > 0: row["answer"] = finalBase.ix[result.iloc[0].name]["out"]

    return entity