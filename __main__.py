#!/usr/bin/env python
# encoding=utf8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from uuid import uuid4

from ali import Ali
from executor import EXECUTORS

''' 执行入口
'''


def main():
    """The main entry
    """
    aliId      =  str(uuid4())
    
    ali = Ali(aliId)
    try:
        
        #注册运算实例
        ip     =  '127.0.0.1'
        ali.reg(ip)

        #开启计算
        executors = dict(map(lambda x: (x.id, x()), EXECUTORS))
        ali.run(executors)

    except KeyboardInterrupt:
        # Ctrl + C
        ali.cancel()
        pass
        

sys.exit(main())

 





