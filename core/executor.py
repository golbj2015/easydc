# encoding=utf8
# The task base
import gevent
import string  
import hashlib 
import random
 
class TaskExecutor(object):
    
    ali = None 
    def __call__(self,opType, task):

        if opType=='compute':
            '''计算子任务
            '''
            pass
        elif opType=='merge':
            '''合并任务
            '''
            pass
        
        raise NotImplementedError
