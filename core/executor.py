# encoding=utf8
# The task base
import gevent
import string  
import hashlib 
import random

''' 执行任务基类
    
    业务代码需要继承此类
'''
 
class TaskExecutor(object):
    
    #运算实例
    ali = None 

    def compute(self,task):
        '''计算子任务
            task － 子任务
        '''
        raise NotImplementedError

    def merge(self,tasks):
        '''合并任务
            tasks － 子任务列表
        '''
        raise NotImplementedError

 