from sqlalchemy.exc import ProgrammingError
from sqlalchemy import create_engine

from util import textUtil as tu
import re
import pandas as pd
from string import punctuation

class GraphDB(object):

    global core
    global dbengine

    global category
    global input
    global output
    global core

    global simpPunctuation

    def __init__(self, url_database, core):
        self.category = "category"
        self.input = "input"
        self.output = "output"
        self.core = core
        self.connectToDB(url_database)
        self.simpPunctuation =  "!,.:;?"

    def connectToDB(self,url_database):
        try:
            self.dbengine = create_engine('postgresql://'+url_database)
        except ProgrammingError:
            exit(127)

    def queryByCategory(self,category):
        base = pd.read_sql_query('select * from "learnpair" where LOWER(category) like {}'.format("'%%"+category+"%%'"), con=self.dbengine)
        base.drop('id', axis=1, inplace=True)
        base.drop('createddate', axis=1, inplace=True)
        base.drop('userid', axis=1, inplace=True)
        base[self.category] = base[self.category].apply(lambda x: tu.removeSamples(x, self.core).lower())

        base = base.loc[base[self.category] == category]

        base[self.input] = base[self.input].apply(lambda x: tu.prepreGraphText(x))
        base = base.drop_duplicates(subset=[self.category,self.input])

        return base

    def queryByCategoryDropDuplicates(self,category):
        base = pd.read_sql_query('select * from "learnpair" where LOWER(category) like {}'.format("'%%"+category+"%%'"), con=self.dbengine)
        base.drop('id', axis=1, inplace=True)
        base.drop('createddate', axis=1, inplace=True)
        base.drop('userid', axis=1, inplace=True)
        base[self.category] = base[self.category].apply(lambda x: tu.removeSamples(x, self.core).lower())

        base = base.loc[base[self.category] == category]

        base[self.input] = base[self.input].apply(lambda x: tu.prepreGraphText(x))
        base[self.output] = base[self.output].apply(lambda x: tu.regexClean(x))
        base = base.drop_duplicates(subset=[self.category,self.input,self.output])

        return base


    def searchBaseInFieldCust(self,type,base,text,strong=True):
        if strong:
            base = base.loc[base[type] == text]
            base = base.drop_duplicates(subset=[self.category,self.input,self.output])
            return base
        return base[base[type].str.contains(text, na=False)]

    def search(self,categoryBase,entity,strong=True):
        entity = [{"entity": x, "answer": []} for x in entity]

        for row in entity:
            _rowdata = row["entity"].lower()
            result = self.searchBaseInFieldCust(self.input, categoryBase, _rowdata,strong)
            if len(result) > 0: row["answer"] = [item[self.output] for i, item in result.iterrows()]

        return entity

    def isCatExist(self,category):
        base = pd.read_sql_query(
            'select count(*)>0  as exist from "learnpair" where LOWER(category) like {}'.format("'%%" + category + "%%'"),
            con=self.dbengine)
        return base['exist'][0]

    def getCategoryList(self):
        base = pd.read_sql_query(
            'select lower(category) as category from "learnpair" where length(category)>0 group by category order by category',
            con=self.dbengine)

        base[self.category] = base[self.category].apply(lambda x: tu.removeSamples(x, self.core).lower().rstrip(self.simpPunctuation))
        base = base.drop_duplicates(subset=[self.category])

        maxLen = 0

        for i, item in base.iterrows():
            currLen = len(item['category'])
            if currLen > maxLen:
                maxLen = currLen

        return base,maxLen