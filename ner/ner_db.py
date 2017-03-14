#! /usr/bin/env python
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from sqlalchemy.exc import ProgrammingError

from util import textUtil as tu
import re
from sqlalchemy import create_engine
import datetime

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

    global isGraph

    def __init__(self,url_database,core,connectToDdBool=False,isGraph=False):
        self.core = core
        self.maxLenChar = 0
        self.setParameters(url_database,connectToDdBool)
        self.isGraph = isGraph
        self.reConnectToDb()

    def setParameters(self,url_database,connectToDdBool=False):
        self.connectToDdBool = connectToDdBool
        self.url_database = url_database

    def reConnectToDb(self):
        self.category = "category"
        self.input = "input"
        self.output = "output"

        if self.connectToDdBool:
            self.connectToDB('postgresql://'+self.url_database)
        else:
            self.connectToExel(self.url_database)

        self.prepareBase()
        self.maxLenChar = self.base[self.input].map(lambda x: len(x)).max()
        print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"[URL DATABASE]",self.url_database)
        print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"[CONNECT TO DB]",self.connectToDdBool)

    def initEmptyDB(self):
        self.base = pd.DataFrame(columns=[self.category,self.input,self.output])

    def getRaw(self,text):
        if self.isGraph:
            return tu.getRawSpace(text, self.core)
        else:
            return tu.getRaw(text, self.core)

    def prepareBase(self):
        self.base['orig'] = self.base[self.input]
        self.base = self.base.fillna(value='')
        self.base[self.input] = self.base[self.input].apply(lambda x: self.getRaw(x))
        self.base['orig'] = self.base['orig'].apply(lambda x: re.sub("[\s]+", " ", x))
        self.base[self.category] = self.base[self.category].apply(lambda x: self.getRaw( tu.removeSamples(x,  self.core).strip()))
        self.base[self.output] = self.base[self.output].apply(lambda x: tu.prepareSuperscript(x))

        if self.isGraph:
            # print ("self.base",len(self.base))
            self.base = self.base.drop_duplicates(subset=['category','input'])
            # print("temp_baze",len(temp_baze))
        else:
            self.base = self.base.drop_duplicates(subset=['category', 'input','output'])

    def connectToExel(self, url_database):
        self.base = pd.read_excel(url_database, sheetname=0, header=None, names=[self.category, self.input, self.output])

    def connectToDB(self,url_database):
        try:
            engine = create_engine(url_database)
            base = pd.read_sql_query('select * from "learnpair"', con=engine)
            base.drop('id', axis=1, inplace=True)
            base.drop('createddate', axis=1, inplace=True)
            base.drop('userid', axis=1, inplace=True)
            self.base = base
        except ProgrammingError:
            self.initEmptyDB()

    def searchBaseInField(self,type, text):
        return self.base.loc[self.base[type] == text]

    def searchBaseInFieldCust(self,type,base,text,strong=True):
        if strong:
            return base.loc[base[type] == text]
        return base[base[type].str.contains(text, na=False)]

    def search(self, category, entity, strong=True):
        entity = [{"entity": x, "answer": []} for x in entity]

        category = tu.removeSamples(category,  self.core).strip()
        category = self.getRaw(category)

        if len(category.strip()) > 0:
            finalBase = self.searchBaseInField(self.category, category)
            if len(finalBase) == 0: return entity
        else:
            return entity

        for row in entity:
            result = self.searchBaseInFieldCust(self.input, finalBase, self.getRaw(row["entity"]),strong)
            if len(result) > 0: row["answer"] = [item[self.output] for i, item in result.iterrows()]
        return entity

    def getBaseByCat(self, category):
        category = tu.removeSamples(category, self.core).strip()
        category = self.getRaw(category)
        return self.searchBaseInField(self.category, category)

    def isInputExist(self,type, text):
        if type == self.category:
            text = tu.removeSamples(text, self.core).strip()
        text = self.getRaw(text)

        if len(text) == 0: return False
        result = self.searchBaseInField(type, text)
        return len(result) > 0