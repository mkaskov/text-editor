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
    base['in'] = base['in'].apply(lambda x:  tu.getRaw(x.encode("utf-8"), core))
    base['category'] = base['category'].apply(lambda x:  tu.getRaw(x.encode("utf-8"), core))
    return base

def searchBaseInField(type, db, text): return db.loc[db[type] == text]

def search(dataBase, category, entity, core):
    entity = [{"entity":x,"answer":""} for x in entity]

    category = tu.removeSamples(category, core).strip()
    category = tu.getRaw(category, core)

    if len(category.strip()) > 0:
        finalBase = searchBaseInField('category',dataBase,category)
        if len(finalBase) == 0: return entity
    else: return entity

    for row in entity:
        result = searchBaseInField('in',finalBase,tu.getRaw(row["entity"], core))
        if len(result) > 0: row["answer"] = [item["out"].encode("utf-8") for i,item in result.iterrows()]
    return entity

def isInputExist(type, db, text, core):
    if type == "category":
        text = tu.removeSamples(text, core).strip()
    text = tu.getRaw(text, core)

    if len(text)==0: return False
    result = searchBaseInField(type, db, text)
    return len(result) > 0

