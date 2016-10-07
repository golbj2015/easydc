#!/usr/bin/env python
# encoding=utf8

import logging
import gevent
import copy
from gevent.pool import Pool
from uuid import uuid4
from model import Model
from const import *
from alu import *

''' 运算实例基类
  一个运算进程（对应一个docker实例） 每个进程有唯一的编号:ALIID

'''
class Ali(Model):
    ''' 运算实例基类
        功能：1. 实例注册
             2. 实例注销
             3. 实例心跳 用于keep alive
             4. 子任务运算
             5. 合并运算

            Follower负责
             6.选举权 

            Leader负责
             7.任务分派
             8. 结果分派
             9. 实例检查
            10. 任务检查

        结构：
             aliId  实例唯一编号  注册时产生
             cpu    cpu个数
             mem    内存大小 单位MB
             io     磁盘io 作为参考
             thNum  子任务计算线程数 同时可以处理多个Subtask
             runNum  当前线程数 在计算中的线程
             status    状态  normal－正常  abnormal－异常
             weight    权重 控制任务分配
             runCount  运算任务次数
             aliType       类型  Leader  Follower
    '''
   
    def __init__(self,aliId,threadNum=5):
        '''初始化

           aliId - 实例id 唯一值 可以使用uuid4()生成
           threadNum - 处理计算的线程数
        '''
        super(Ali, self).__init__()
        self.Name = "Ali"

        self.threadNum = threadNum

        #初始化运算单元
        self.aluTaskAllot  =  AluTaskAllot(aliId)
        self.aluCompute    =  AluCompute(aliId)
        self.aluHeartBeat  =  AluHeartBeat(aliId)
        self.aluCheckAli   =  AluCheckAli(aliId)
        self.aluCheckTask  =  AluCheckTask(aliId)

        #记录线程
        self.jobs = []

        self.aliData = None
        self.aliId = aliId
        self.aliType = ALI_TYPE_FOLLOWER

        #强制完成的任务
        self.finishedPtask = []
        


    # 基础功能////////////////////////////////////////////////
    def reg(self,ip,weight=0):
        ''' 实例注册 
            服务启动时注册，只可以注册一次 由主线程处理
            
            参数：
                ip - 服务器IP
                weight - 子任务分派权重
        '''
        data = {
            'aliId' : self.aliId,
            'ip'    : ip,
            'cpu'   : 1,              
            'mem'   : 10240,           
            'io'    : '',
            'thNum' : self.threadNum,
            'runNum': 0,
            'status': ALI_STATUS_NORMAL,
            'weight': weight,
            'runCount': 0,
            'aliType': ALI_TYPE_FOLLOWER

        }
        self.addModel(self.Name,data,'aliId')

        return data
        
    def cancel(self):
        '''实例注销  更改实例状态为无效
           服务关闭时执行  由主线程处理
        '''
        idFilter   = {'_id' : self.aliId}
        updateData = {'status' : ALI_STATUS_ABNORMAL,
                      'aliType' : ALI_TYPE_FOLLOWER 
            }
        self.updateModel(self.Name,idFilter,updateData)

        #重置任务
        updateCond = {'aliId':self.aliId,
                'status':{"$in":[TASK_STATUS_ALLOTED,TASK_STATUS_COMPUTING]}}
        self.updateModel('TaskQuere',updateCond,{'status':TASK_STATUS_SPLITED})

        return True

    def run(self,executors):
        ''' 执行入口
        '''
        #开启心跳
        self._heartbeat()

        #实例检查
        self._checkAli()

        #任务检查
        self._checkTask()

        #任务分派
        self._allotTask()

        #开启计算功能
        self._compute(executors)

        #等待任务执行
        self._waitall()

    def checkFinished(self,ptaskId):
        '''检查是否完成  对外接口
        '''
        if ptaskId in self.finishedPtask:
            return True

        return False

    def finishPTask(self,ptaskId):
        '''强制关闭任务 对外接口
        '''
        self.updateModel('PTask',{'_id':ptaskId},{'status':TASK_STATUS_COMPUTED})

    def updateProcess(self,taskId,process):
        '''更新进度
           process 进度
        ''' 
        self.updateModel('SubTask',{'_id':taskId},{'process':process})


    def _heartbeat(self):
        '''发起心跳  
          功能：
            1.ALI 会定时反馈一个消息表示自己还有效 
            2.检查Leader是否有效 如果无效发启选举
        '''
        self.jobs.append(gevent.spawn(self.aluHeartBeat.run,self))

    def _compute(self,executors):
        ''' 子任务运算 
            多个线程同时处理子任务

            executors - 用户计算实现
               {'bizType':executor}

        '''
        aliPool = Pool(self.threadNum)

        #self.jobs.append(aliPool.spawn(self.aluCompute.run,executors))

        def getQuere(obj,executors,pool,aliObj):

            while True:
                
                #查询任务队列获取待运算的任务
                query = {
                    'status':TASK_STATUS_ALLOTED,
                    'aliId' :obj.aliId
                }
                taskQueres = obj.getModels('TaskQuere',query,100)

                if taskQueres.count() == 0:
                    gevent.sleep(SLEEP_NO_COMPUTETASK)
                    #print "compute.getQuere no data sleep 5s"
                    continue 

                for taskQuere in taskQueres:

                    taskType = taskQuere['taskType']
                    computeType = COMPUTE_TYPE_COMPUTE
                    if taskType == TASK_TYPE_SUB:
                        # 查询subtask
                        taskInfo = obj.getModel('SubTask',{'_id':taskQuere['taskId']})
                    elif taskType == TASK_TYPE_PARENT:
                        # 查询父任务
                        taskInfo = obj.getModel('PTask',{'_id':taskQuere['taskId']})

                        computeType = COMPUTE_TYPE_MERGE
                    else:
                        raise ValueError('taskType:%s error'%taskType)

                    executorObj = executors.get(taskInfo['bizType'])
                    if executorObj:
                        #避免多线程 资源共享问题
                        executor = copy.deepcopy(executorObj)
                        executor.ali = aliObj
                        while pool.full():
                            #print "compute pool full sleep 3s"
                            gevent.sleep(SLEEP_POOL_FULL)

                        pool.spawn(obj.aluCompute.run,executor,computeType,taskInfo)

                gevent.sleep(0)

        self.jobs.append(gevent.spawn(getQuere,self,executors,aliPool,self))

    # Leader负责/////////////////////////////////////////////

    def _allotTask(self):
        ''' 任务分派 

          操作：
             TaskQuere.status = alloted
             TaskQuere.aliId  = aliId

          由单独线程处理 

        '''

        self.jobs.append(gevent.spawn(self.aluTaskAllot.run,self))

    def _checkAli(self):
        ''' 检查实例 Leader负责管理各个Follower状态
        '''
        self.jobs.append(gevent.spawn(self.aluCheckAli.run,self))

    def _checkTask(self):
        ''' 检查任务 
            需要定时检查任务是否有效，对于僵尸的任务需要重新分派AUI,由Leader负责处理
        '''
        self.jobs.append(gevent.spawn(self.aluCheckTask.run,self))

 
    #公共区域/////////////////////////////////////////////////

    def _waitall(self):
        '''等待任务执行
        '''
        gevent.joinall(self.jobs)



 
