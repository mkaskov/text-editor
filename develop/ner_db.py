#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from util import textUtil as tu
from nnet import data_utils as du
import re

import pandas as pd


class NerDB(object):

    global base
    global maxLenChar

    def __init__(self,url_database,core):
        self.connectToBase(url_database,core)
        self.maxLenChar = self.base['in'].map(len).max()

    def connectToBase(self,url_database,core):
        base = pd.read_excel(url_database, sheetname=0, header=None, names=['category', 'in', 'out'])
        base['in_orig'] = base['in']
        base = base.fillna(value='')
        base['in'] = base['in'].apply(lambda x:  tu.getRaw(x.encode("utf-8"),core))
        base['in_orig'] = base['in_orig'].apply(lambda x: re.sub("[\s]+", " ", x.encode("utf-8")))
        base['category'] = base['category'].apply(lambda x:  tu.getRaw(x.encode("utf-8"),core))
        self.base = base

    def getRaw(self,text):
        return "".join([x for x in du.tokenizer_tpp(text, self._TTP_WORD_SPLIT) if x not in tu.dotsArrEntity])

    def searchBaseInField(self,type, text):
        return self.base.loc[self.base[type] == text]

    def searchBaseInFieldCust(self,type,base, text):
        return base.loc[base[type] == text]

    def search(self, category, entity, core):
        entity = [{"entity": x, "answer": ""} for x in entity]

        category = tu.removeSamples(category, core).strip()
        category = tu.getRaw(category, core)

        if len(category.strip()) > 0:
            finalBase = self.searchBaseInField('category', category)
            if len(finalBase) == 0: return entity
        else:
            return entity

        for row in entity:
            result = self.searchBaseInFieldCust('in', finalBase, tu.getRaw(row["entity"], core))
            if len(result) > 0: row["answer"] = [item["out"].encode("utf-8") for i, item in result.iterrows()]
        return entity

    def isInputExist(self,type, text, core):
        if type == "category":
            text = tu.removeSamples(text, core).strip()
        text = tu.getRaw(text, core)

        if len(text) == 0: return False
        result = self.searchBaseInField(type, text)
        return len(result) > 0