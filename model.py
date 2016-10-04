#!/usr/bin/env python
# encoding=utf8

import logging
import time
import copy
import pymongo
from datetime import datetime

from const import *


''' 数据源
'''
class Model(object):
    ''' 数据源 使用mongodb存放   
    '''

    def __init__(self):
        '''初始化
        '''
        self.db = None
        with pymongo.MongoClient(host =  DC_MONGO_HOST, port = DC_MONGO_PORT) as mongo:
            self.db = mongo.easydc

    def getModel(self,tableName,filterCond):
        '''查询一条数据
        '''
        return self.db[tableName].find_one(filterCond)

    def getModels(self,tableName,filterCond,limits):
        '''查询多条数据
        '''
        return self.db[tableName].find(filterCond,limit=limits,sort=[ ('addtime', 1) ])
        
    def addModel(self,tableName,addData,pkField=None):
        '''新增一条数据
        '''
        if pkField and addData.has_key(pkField):
            addData['_id'] = addData[pkField]
        addData['addtime'] = datetime.now()
        return self.db[tableName].insert_one(addData).inserted_id


    def addModels(self,tableName,addDatas,pkField=None):
        '''新增多条数据
        '''
        
        for addData in addDatas:
            addData['addtime'] = datetime.now()
            if pkField and addData.has_key(pkField):
                addData['_id'] = addData[pkField]

        result = self.db[tableName].insert_many(addDatas)

        return result.inserted_ids

    def updateModel(self,tableName,filterCond,updateData):
        '''更新一条数据
        '''

        updateData['updatetime'] = datetime.now()
        result = self.db[tableName].update_one(filterCond,{ '$set': updateData })
        return result.matched_count,result.modified_count

    def updateModels(self,tableName,filterCond,updateData):
        '''更新多条数据
        '''
        
        updateData['updatetime'] = datetime.now()
        result = self.db[tableName].update_many(filterCond,{'$set': updateData } )

        return result.matched_count,result.modified_count

    
