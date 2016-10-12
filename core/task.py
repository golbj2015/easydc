#!/usr/bin/env python
# encoding=utf8

import logging
from model import Model

from const import *

 
''' Task 管理
'''

class TaskQuere(Model):
    ''' 任务队列   

        结构：
          taskId    － 任务id 子任务和父任务公用 唯一键
          taskType  － 任务类型 subtask ptask 
          status    － 状态
          aliId     － 实例id
          tryCount  － 重试次数

    '''

   
    def __init__(self):
        '''初始化
        '''
        super(TaskQuere, self).__init__()

        self.Name = "TaskQuere"

        
    def push(self,datas):
        '''加入队列 状态为已分割
        '''
     
        self.addModels(self.Name,datas,'taskId')

        
class PTask(Model):
    ''' 父任务 

        结构：
          PTaskId － 父任务id
          bizType － 业务类型
          status  － 状态
          process － 进度
          errInfo － 异常信息
          bizInfo － 业务信息
 
    '''
   
    def __init__(self):
        '''初始化
        '''
        super(PTask, self).__init__()

        self.Name = "PTask"

    def add(self,data):
        ''' 新增父任务
        '''
        self.addModel(self.Name,data,'PTaskId')
        
 


class SubTask(Model):
    ''' 子任务 
        结构：
            SubTaskId － 子任务id
            PTaskId   － 父任务id
            bizType   － 业务类型
            status    － 状态 
            tryCount  － 重试次数
            bizInfo   － 业务信息
            process   － 进度
            errInfo   － 异常信息
    '''
   
    def __init__(self):
        '''初始化
        '''
        super(SubTask, self).__init__()
        self.Name = "SubTask"

    def add(self,datas):
        '''新增子任务
        '''
        self.addModels(self.Name,datas,'SubTaskId')



    
