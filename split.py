#!/usr/bin/env python
# encoding=utf8

''' 任务分割
    
    python split.py
'''

from core import TaskSplit

def splitTask():
    ''' 分割方法
    '''
    taskSplit = TaskSplit()

    bizType      =  'edc.crackmd5'
    bizPtask     =  'crack md5 len: 6'

    md5 = '07481d311ef2d591082feb978189744d' #MvCh

    bizSubTasks  =  [
                {'md5':md5,'md5len':4},
                {'md5':md5,'md5len':4},
                {'md5':md5,'md5len':4},
                {'md5':md5,'md5len':4},
                {'md5':md5,'md5len':4}
            ]

    ret,msg = taskSplit.run(bizType,bizPtask,bizSubTasks)

    print ret,msg

if __name__ == '__main__':
    splitTask()
