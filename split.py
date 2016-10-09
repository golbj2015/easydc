#!/usr/bin/env python
# encoding=utf8

import time
from uuid import uuid4

from task import *
from const import *
from logger import EdcLogger as Logger


''' 任务分割管理
'''
class TaskSplit(object):
    ''' 任务分割   
    '''
   
    def __init__(self):
        '''初始化
        '''
        pass

    def run(self,bizType,bizPtask,bizSubTasks,tryCount = 0):
        '''执行分割 写入数据库中
           参数：
            bizType  业务类型 
            subTasks 子任务列表 业务信息
            tryCount  失败重试次数
        '''

        ptaskId  = str(uuid4())
        #父任务
        ptaskData = {
            'PTaskId' : ptaskId,
            'bizType' : bizType,
            'status'  : TASK_STATUS_SPLITED,
            'bizInfo' : bizPtask

        }
        
        #子任务
        subTaskDatas = []
        taskQueres   = []

        for bizData in bizSubTasks:

            subTaskId = str(uuid4())
            subTaskDatas.append({
                'SubTaskId' : subTaskId,
                'PTaskId'   : ptaskId,
                'bizType'   : bizType,
                #'status'    : status,
                'tryCount'  : tryCount,
                'bizInfo'   : bizData
                })

            taskQueres.append({
                'taskId'    : subTaskId,
                'PTaskId'   : ptaskId,
                'taskType'  : TASK_TYPE_SUB,
                'status'    : TASK_STATUS_SPLITED
                })
        try:
            #添加父任务
            PTask().add(ptaskData)

            #添加子任务
            SubTask().add(subTaskDatas)

            #加入队列
            TaskQuere().push(taskQueres)

            Logger.log("split","分割为%d个子任务"%len(bizSubTasks),ptaskId=ptaskId)

        except Exception,e:

            Logger.log("split","分割失败 原因:%s"%str(e),info=bizSubTasks,ptaskId=ptaskId,logType=LOG_LEVEL_ERROR)
            return False,str(e)

        return True,'Success'


          



