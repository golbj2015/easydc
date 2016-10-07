#!/usr/bin/env python
# encoding=utf8

''' 运算实例单元测试
  测试命令 python -m unittest -v ali_test.TestAli
'''

import unittest
import json
import sys

sys.path.append("..")
from ali import Ali
from executor import EXECUTORS


class TestAli(unittest.TestCase):

    def setUp(self):
        
        aliId      =  'testreg3'
        ip     =  '127.0.0.1'
        self.ali = Ali(aliId,ip)
 
    def tearDown(self):
        pass
 
 
    def test_reg(self):
        ''' 测试注册方法
        '''
        aliId      =  'testreg2'
        ip     =  '127.0.0.1'

        ret = self.ali.reg(aliId,ip,1,10240,'io')

        self.assertEqual(ret, True)

    def test_cancel(self):
        ''' 测试注销方法
        '''
        ret = self.ali.cancel()

        self.assertEqual(ret, True)

    def test_allotTask(self):
        '''测试分派
        '''
        self.ali._heartbeat()
        self.ali._allotTask()

        self.ali._waitall()

        self.assertEqual(True, True)

    def test_compute(self):
        '''测试计算
        '''
        executors = dict(map(lambda x: (x.id, x()), EXECUTORS))
        self.ali._compute(executors)

        self.ali._waitall()

        self.assertEqual(True, True)

    def test_heardbeat(self):
        '''测试心跳
        '''
        self.ali._heartbeat()
        self.ali._waitall()

        self.assertEqual(True, True)

    def test_checkAli(self):
        '''测试检查实例
        '''
        self.ali._checkAli()
        self.ali._waitall()

        self.assertEqual(True, True)

    def test_checkTask(self):
        '''测试检查任务
        '''
        self.ali._heartbeat()
        self.ali._checkTask()
        self.ali._waitall()

        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
