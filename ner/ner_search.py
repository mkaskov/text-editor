#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from cStringIO import StringIO
from nnet import data_utils
import re

import pandas as pd
import numpy as np

from util import textUtil

def searchInBase(dataBase,category,entity):
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

def getEntityPandas(entityResult):
    entity = pd.DataFrame({"entity": entityResult}, index=np.arange(1, len(entityResult) + 1))
    entity["answer"] = ""
    return entity

def printPandasResultSearch(integrity, category, result):
    if integrity: print("integrity: True")
    else: print("\x1b[31m\"[WARNING] result is not integral\"\x1b[0m")

    if len(category) > 0: print("category: ", category)

    print("\n")

    for index, row in result.iterrows():
        print("[]", row["entity"])
        print("  -- []", row["answer"])

    # result

def getSimpleEntity(result):
    retValue = []
    for index, row in result.iterrows():
        retValue.append({"entity":row['entity'],"answer":row['answer']})

    return retValue


def search(dataBase,integrity,categoryResult,entityResult,core_):
    global core
    core = core_

    category = ""
    if len(categoryResult) > 0: category = categoryResult[0]

    entity = getEntityPandas(entityResult)

    searchResultEntity = searchInBase(dataBase,category,entity)

    # printPandasResultSearch(integrity, category, searchResultEntity)

    return getSimpleEntity(searchResultEntity)


    # for index, row in entity.iterrows():
    #     if len(row["answer"]) == 0:
    #         parsedText = nerParser(row["entity"])
    #         print("integrity:", parsedText["_integrity"])
    #
    #         if len(parsedText["category"]) > 0: print("category:", parsedText["category"])
    #
    #         for x in parsedText["entity"]: print(x)