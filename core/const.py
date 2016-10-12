# encoding=utf8

from db import *
"""
  常量
"""
#任务状态
TASK_STATUS_SPLITED = 'splited'     #已分割
TASK_STATUS_ALLOTED = 'alloted'     #已分派
TASK_STATUS_COMPUTING = 'computing' #运算中
TASK_STATUS_COMPUTED = 'computed'   #运算完
TASK_STATUS_MERGEING = 'merging'    #待合并
TASK_STATUS_COMPELED = 'completed'  #已完成
TASK_STATUS_CANCAL   = 'cancel'     #取消
TASK_STATUS_FAILED   = 'failed'     #失败

#任务类型
TASK_TYPE_SUB = 'subtask'           #子任务
TASK_TYPE_PARENT = 'ptask'          #父任务

#实例类型
ALI_TYPE_LEADER = 'Leader'          #Leader
ALI_TYPE_FOLLOWER = 'Follower'      #Follower

#实例状态
ALI_STATUS_NORMAL = 'normal'        #正常    
ALI_STATUS_ABNORMAL = 'abnormal'    #异常

#运算类型
COMPUTE_TYPE_COMPUTE = 'compute'    #运算
COMPUTE_TYPE_MERGE = 'merge'        #合并

#间隔配置
SLEEP_NOT_LEADER = 10         #检查是否为Leader 
SLEEP_NO_ALLOTTASK = 3        #没有待分派的任务
SLEEP_HEARTBEAT  = 3          #心跳间隔
SLEEP_CHECK_ALI  = 10         #检查实例
SLEEP_CHECK_TASK  = 60        #检查任务
SLEEP_NO_COMPUTETASK = 5      #没有待计算任务
SLEEP_POOL_FULL    = 3        #线程池满了

#日志级别
LOG_LEVEL_DEBUG = 'debug'
LOG_LEVEL_INFO = 'info'
LOG_LEVEL_ERROR = 'error'
LOG_LEVEL_WARN = 'warn'



#Mongodb 配置
DC_MONGO_HOST = MONGO_HOST
DC_MONGO_PORT = MONGO_PORT
