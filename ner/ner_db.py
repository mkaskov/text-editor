#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from util import textUtil as tu
from nnet import data_utils as du
import re
from sqlalchemy import create_engine
import threading

import pandas as pd


class NerDB(object):

    global base
    global maxLenChar

    global category
    global input
    global output
    global core

    global url_database
    global connectToDdBool

    def __init__(self,url_database,core,connectToDdBool=False):
        self.core = core
        self.connectToDdBool = connectToDdBool
        self.url_database = url_database
        self.reConnectToDb()

    def reConnectToDb(self):
        if self.connectToDdBool:
            self.category = "category"
            self.input = "input"
            self.output = "output"
            self.connectToDB('postgresql://'+self.url_database)
        else:
            self.category = "category"
            self.input = "in"
            self.output = "out"
            self.connectToExel(self.url_database)

        self.prepareBase()

        self.maxLenChar = self.base[self.input].map(lambda x: len(x.decode("utf-8"))).max()
        print (self.base)
        # threading.Timer(60, self.reConnectToDb()).start()

    def prepareBase(self):
        self.base['orig'] = self.base[self.input]
        self.base = self.base.fillna(value='')
        self.base[self.input] = self.base[self.input].apply(lambda x: tu.getRaw(x.encode("utf-8"), self.core))
        self.base['orig'] = self.base['orig'].apply(lambda x: re.sub("[\s]+", " ", x.encode("utf-8")))
        self.base[self.category] = self.base[self.category].apply(lambda x: tu.getRaw(x.encode("utf-8"), self.core))

    def connectToExel(self, url_database):
        self.base = pd.read_excel(url_database, sheetname=0, header=None, names=[self.category, self.input, self.output])

    def connectToDB(self,url_database):
        engine = create_engine(url_database)
        base = pd.read_sql_query('select * from "learnpair"', con=engine)
        base.drop('id', axis=1, inplace=True)
        base.drop('createddate', axis=1, inplace=True)
        base.drop('userid', axis=1, inplace=True)
        self.base = base

    def getRaw(self,text):
        return "".join([x for x in du.tokenizer_tpp(text, self._TTP_WORD_SPLIT) if x not in tu.dotsArrEntity])

    def searchBaseInField(self,type, text):
        return self.base.loc[self.base[type] == text]

    def searchBaseInFieldCust(self,type,base,text,strong=True):
        if strong:
            return base.loc[base[type] == text]
        return base[base[type].str.contains(text, na=False)]

    def search(self, category, entity, strong=True):
        entity = [{"entity": x, "answer": ""} for x in entity]

        category = tu.removeSamples(category,  self.core).strip()
        category = tu.getRaw(category,  self.core)

        if len(category.strip()) > 0:
            finalBase = self.searchBaseInField(self.category, category)
            if len(finalBase) == 0: return entity
        else:
            return entity

        for row in entity:
            result = self.searchBaseInFieldCust(self.input, finalBase, tu.getRaw(row["entity"],self.core),strong)
            if len(result) > 0: row["answer"] = [item[self.output].encode("utf-8") for i, item in result.iterrows()]
        return entity

    def isInputExist(self,type, text):
        if type == self.category:
            text = tu.removeSamples(text, self.core).strip()
        text = tu.getRaw(text, self.core)

        if len(text) == 0: return False
        result = self.searchBaseInField(type, text)
        return len(result) > 0