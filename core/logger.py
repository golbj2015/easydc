# encoding=utf8
# The task base

from model import Model

from const import *

 
''' 日志管理
'''

class EdcLogger(object):
    ''' 日志管理   

        结构：
            opName - 操作名称
            logContent - 日志内容
            logType - 日志类型 debug info error warn
            aliId   - 实例ID
            ptaskId - 父任务ID
            addTime - 时间
    '''
   
    def __init__(self):
        '''初始化
        '''
        pass

    @classmethod
    def log(cls,opName,logContent,info=None,aliId='',ptaskId='',logType=LOG_LEVEL_INFO):
        ''' 记录日志
        '''
        logData = {
            'opName'     : opName,
            'logContent' : logContent,
            'logType'    : logType,
            'aliId'      : aliId,
            'ptaskId'    : ptaskId,
            'info'       : info
        }

        model = Model()
        model.addModel('Logger',logData)

