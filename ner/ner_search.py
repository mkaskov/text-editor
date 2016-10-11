#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ner import ner_db

import pandas as pd
import numpy as np

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

def getSimpleEntity(result):
    retValue = []
    for index, row in result.iterrows():
        retValue.append({"entity":row['entity'],"answer":row['answer']})

    return retValue

def checkResolved(entity):
    for item in entity:
        if len(item['answer'])==0: return False
    return True

def search(dataBase,integrity,categoryResult,entityResult,core_):
    global core
    core = core_

    category = categoryResult[0] if len(categoryResult) > 0 else ""
    entity = getEntityPandas(entityResult)
    searchResultEntity = ner_db.searchInBase(dataBase,category,entity,core)

    entity = getSimpleEntity(searchResultEntity)
    resolved = checkResolved(entity)

    # printPandasResultSearch(integrity, category, searchResultEntity)

    return entity,resolved


    # for index, row in entity.iterrows():
    #     if len(row["answer"]) == 0:
    #         parsedText = nerParser(row["entity"])
    #         print("integrity:", parsedText["_integrity"])
    #
    #         if len(parsedText["category"]) > 0: print("category:", parsedText["category"])
    #
    #         for x in parsedText["entity"]: print(x)