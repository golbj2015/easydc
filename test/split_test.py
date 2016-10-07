#!/usr/bin/env python
# encoding=utf8

''' 分割功能单元测试
  测试命令 python -m unittest -v split_test.TestTaskSplit
'''

import unittest
import json
import sys

sys.path.append("..")
from split import TaskSplit

class TestTaskSplit(unittest.TestCase):

    def setUp(self):
 
        self.taskSplit = TaskSplit()
 
    def tearDown(self):
        pass
 
 
    def test_run(self):
        ''' 测试分割方法
        '''
        '''
        bizType      =  'edc.echo'
        bizPtask     =  'echo task'
        bizSubTasks  =  ['11','21','31','22','33','44','55',"66",'77','88']
        '''

        bizType      =  'edc.crackmd5'
        bizPtask     =  'crack md5 len: 6'

        md5 = '09191f6b5a9c4b452b53735b85e3f55d' #a3L
        
        bizSubTasks  =  [
                    {'md5':md5,'md5len':3},
                    {'md5':md5,'md5len':3}
                ]

        ret = self.taskSplit.run(bizType,bizPtask,bizSubTasks)

        self.assertEqual(ret, True)

if __name__ == '__main__':
    unittest.main()
