#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ner import ner_db

import pandas as pd
import numpy as np
import re

def getEntityPandas(entityResult):
    entity = pd.DataFrame({"entity": entityResult}, index=np.arange(1, len(entityResult) + 1))
    entity["answer"] = ""
    return entity

def getSimpleEntity(result):
    retValue = []
    for index, row in result.iterrows(): retValue.append({"entity":row['entity'],"answer":row['answer']})
    return retValue

def search(dataBase,category,entityResult,core_):
    global core
    core = core_
    entity = getEntityPandas(entityResult)
    searchResultEntity = ner_db.searchInBase(dataBase,category,entity,core)
    return getSimpleEntity(searchResultEntity)

def isCategoryExist(dataBase,category,core):
    check = re.sub("[\s\xA0]+", "", category.decode('utf-8'))
    if len(check)==0: return False
    result = ner_db.searchCategory(dataBase,category,core)
    return len(result) > 0

