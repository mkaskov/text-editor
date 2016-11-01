#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from util import textUtil as tu

import pandas as pd

def connectToBase(url_database,core):
    base = pd.read_excel(url_database, sheetname=0, header=None, names=['category', 'in', 'out'])
    base = base.fillna(value='')
    base['in'] = base['in'].apply(lambda x:  tu.getSearchValue(x.encode("utf-8"),core))
    base['category'] = base['category'].apply(lambda x:  tu.getSearchValue(x.encode("utf-8"),core))
    return base

def searchBaseInField(type, dataBase, text, core):
    return dataBase.loc[dataBase[type] == tu.getSearchValue(text, core)]

def search(dataBase, category, entity, core):
    entity = [{"entity":x,"answer":""} for x in entity]

    if len(category.strip()) > 0:
        finalBase = searchBaseInField('category',dataBase,category,core)
        if len(finalBase) == 0: return entity
    else: return entity

    for row in entity:
        result = searchBaseInField('in',finalBase,row["entity"],core)
        if len(result) > 0: row["answer"] = finalBase.ix[result.iloc[0].name]["out"]

    return entity

def isCategoryExist(dataBase,text,core):
    if len(tu.getSearchValue(text, core))==0: return False
    result = searchBaseInField("category",dataBase,text,core)
    return len(result) > 0

def isInputExist(dataBase,text,core):
    if len(tu.getSearchValue(text, core))==0: return False
    result = searchBaseInField("in",dataBase,text,core)
    return len(result) > 0

