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
        bizType      =  'edc.echo'
        bizPtask     =  'echo task'
        bizSubTasks  =  ['11','21','31','22','33','44','55',"66",'77','88']

        ret = self.taskSplit.run(bizType,bizPtask,bizSubTasks)

        bizType      =  'edc.add'
        bizPtask     =  'add task'
        bizSubTasks  =  ['110','210','310','220','330','440','550','660','770','880']

        ret = self.taskSplit.run(bizType,bizPtask,bizSubTasks)

        self.assertEqual(ret, True)

if __name__ == '__main__':
    unittest.main()
