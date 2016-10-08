#!/usr/bin/env python
# encoding=utf8

import logging
import gevent
import random
import sys
from model import Model
from const import *

''' 运算单元基类
  最小的运算单位 对应一个线程，每个ALI下可以有多个ALU 

'''


class Alu(Model):
    ''' 运算单元基类

        功能： 执行实际的计算功能

    '''
   
    def __init__(self):
        '''初始化
        '''
        super(Alu, self).__init__()
        #类型  任务分派  任务运算 结果分派 选举单元 实例检查 心跳 任务检查
        self.aluType = ''  

    def run(self,params):
        ''' 执行计算
        '''
        pass


class AluTaskAllot(Alu):
    ''' 任务分派运算单元
    '''

    def __init__(self,aliId):
        self.aluType = 'TaskAllot'
        super(AluTaskAllot, self).__init__()

        self.aliId = aliId

    def run(self,obj):
        ''' 执行分派
            操作：
             TaskQuere.status = alloted
             TaskQuere.aliId  = aliId
        '''

        while True:

            #判断是非为Leader 如果不是 sleep 
            if obj.aliType != ALI_TYPE_LEADER:
                gevent.sleep(SLEEP_NOT_LEADER)
                #print "AluTaskAllot not leader sleep 10s"
                continue

            #获取待分派的任务 如果没有任务 sleep 3s
            query = {}
            query['status'] = {"$in":[TASK_STATUS_SPLITED,TASK_STATUS_MERGEING]} 

            tasks = self.getModels('TaskQuere',query,100)

            if tasks.count()==0:
                gevent.sleep(SLEEP_NO_ALLOTTASK)
                #print "AluTaskAllot no data sleep 3s"
                continue

            taskDatas = [task for task in tasks]

            #获取可用的实例
            query = {}
            query['status'] = ALI_STATUS_NORMAL
            alis = self.getModels('Ali',query,100)

            #按照平分规则分派任务 

            #计算每个实例可以分到多少个任务
            taskCount = tasks.count()/alis.count()

            #最少一个任务
            if taskCount==0:taskCount=1

            aliIds = [ali['_id'] for ali in alis]
            #打乱排序
            random.shuffle(aliIds)

            updateTasks = {}
            for ali_id in aliIds:
                i = 0
                for task in taskDatas:
                    if not updateTasks.has_key(task['_id']):
                        updateTasks[task['_id']] = ali_id
                        i+=1

                    if i==taskCount:
                        break

            for key in updateTasks:
                updateData = {'aliId':updateTasks[key],'status':TASK_STATUS_ALLOTED}
                self.updateModel('TaskQuere',{'_id':key},updateData)
            gevent.sleep(1)
            
class AluCompute(Alu):
    ''' 子任务运算单元
    '''

    def __init__(self,aliId):
        self.aluType = 'AluCompute'
        super(AluCompute, self).__init__()

        self.aliId = aliId

    def run(self,executor,computeType,task):
        ''' 执行计算
        '''
        taskId = task['_id']
        #更新子任务状态为 TASK_STATUS_COMPUTING
        self.updateModel('TaskQuere',{'_id':taskId},{'status':TASK_STATUS_COMPUTING})

        if computeType==COMPUTE_TYPE_COMPUTE:
            #执行用户算法
            ptaskId = task['PTaskId']

            result = None
            try:
                result = executor(computeType,task)
            except Exception,e:

                print "subtask %s fail to compute, error message:%s" %(taskId,str(e))
                taskQ = self.getModel('TaskQuere',{'_id':taskId})
                #重试3次
                tryCount = taskQ.get('tryCount',0) + 1
                if tryCount <= 3:
                    self.updateModel('SubTask',{'_id':taskId},{'status':TASK_STATUS_FAILED,'errInfo':str(e)})
                    self.updateModel('TaskQuere',{'_id':taskId},{'tryCount':tryCount,'status':TASK_STATUS_SPLITED})

                    return

            #记录每次运算结果
            self.updateModel('SubTask',{'_id':taskId},{'result':result})

            self.updateModel('TaskQuere',{'_id':taskId},{'status':TASK_STATUS_COMPUTED})

            #检查子任务是否都已经运算完成
            query = {
                     'PTaskId' : ptaskId,
                     'status'  : TASK_STATUS_COMPUTED
                }
            computedTasks = self.getModels('TaskQuere',query,10000)

            query = {
                     'PTaskId' : ptaskId
                }
            allTasks = self.getModels('TaskQuere',query,10000)

            if allTasks.count()==computedTasks.count():

                print 'AluCompute insert %s into quere '%ptaskId
                #加入队列中
                pdata = {
                    'taskId'    : ptaskId,
                    'PTaskId'   : ptaskId,
                    'taskType'  : TASK_TYPE_PARENT,
                    'status'    : TASK_STATUS_MERGEING
                }

                #判断是否已经加入队列
                existData = self.getModel('TaskQuere',{'_id':ptaskId})
                if not existData:
                    self.addModel('TaskQuere',pdata,'taskId')

        else:

            #查询所有子任务结果
            subTasks = self.getModels('SubTask',{'PTaskId' : taskId },1000)
            try:
                executor(computeType,subTasks)
            except Exception,e:
                self.updateModel('PTask',{'_id':taskId},{'status':TASK_STATUS_FAILED,'errInfo':str(e)})
            else:
                #更新子任务状态为TASK_STATUS_COMPELED
                self.updateModel('PTask',{'_id':taskId},{'status':TASK_STATUS_COMPELED})
            
            self.updateModel('TaskQuere',{'_id':taskId},{'status':TASK_STATUS_COMPELED})

class AluHeartBeat(Alu):
    ''' 心跳单元
    '''

    def __init__(self,aliId):
        self.aluType = 'HeartBeat'
        super(AluHeartBeat, self).__init__()

        self.aliId = aliId

    def run(self,obj):
        ''' 开始心跳 
        '''
        beatCount = 0
        leaderBeatPre = 0
        leaderBeatNext = 0

        stepNum = 0
        while True:
            beatCount += 1
            stepNum += 1

            if beatCount > 999999:
                beatCount = 0

            aliData = self.getModel('Ali',self.aliId)
            obj.aliData = aliData
            obj.aliType = aliData['aliType']

            self.updateModel('Ali',{'_id':self.aliId},{'beat':beatCount})

            #检查完成的任务  Leader负责
            self._getPtaskStatus(obj)


            #检查Leader是否还活着
            leaderId = ''
            if stepNum==1:
                leaderBeatPre,leaderId = self._getLeaderBeat()

            if stepNum==3:
                leaderBeatNext,leaderId = self._getLeaderBeat()

            # leader dead
            if stepNum==3 and leaderBeatNext == leaderBeatPre:
                if leaderId:
                    #更改为follower abnormal
                    print "AluHeartBeat leader %s dead"%leaderId
                    self.updateModel('Ali',{'_id':leaderId},{'aliType':ALI_TYPE_FOLLOWER,'status':ALI_STATUS_ABNORMAL})

                    #重置任务
                    updateCond = {'aliId':leaderId,
                            'status':{"$in":[TASK_STATUS_ALLOTED,TASK_STATUS_COMPUTING]}}
                    self.updateModel('TaskQuere',updateCond,{'status':TASK_STATUS_SPLITED})

                #选择一个leader
                leaderBeat,leaderId = self._getLeaderBeat()
                if not leaderId:
                    self._electLeader()

            if stepNum==3:
                #初始化
                stepNum = 0
                leaderBeatNext = 0
                leaderBeatPre =0

            #print "AluHeartBeat aliId:%s beat heard " % self.aliId
            
            #跳动心脏及次数            
            sys.stdout.write("\33[5m\r❤️ %d\033[0m" % beatCount)
            sys.stdout.flush()
            #睡眠3s 再跳动
            gevent.sleep(SLEEP_HEARTBEAT)

    def _getLeaderBeat(self):
        ''' 获取beat数
        '''
        queryCond = {
                'aliType' : ALI_TYPE_LEADER,
                'status'  : ALI_STATUS_NORMAL
            }
        leader = self.getModel('Ali',queryCond)
        if leader:

            return leader.get('beat',0),leader['_id']
        else:
            return 0,''


    def _electLeader(self):
        '''选举一个Leader
        '''
        query = {
                'status' : ALI_STATUS_NORMAL
                }
        alis = self.getModels('Ali',query,1)

        for ali in alis:
            self.updateModel('Ali',{'_id':ali['_id']},{'aliType':ALI_TYPE_LEADER})
            print "AluHeartBeat leader %s selected" % ali['_id']

    def _getPtaskStatus(self,obj):
        '''获得Ptask状态
            如果父任务已经设置为完成，正在运行的子任务需要强制完成
        '''
        query = {
                     'status' : TASK_STATUS_COMPUTING 
                }

        runningTasks = self.getModels('TaskQuere',query,100)

        ptaskIds = list(set([task['PTaskId'] for task in runningTasks]))

        pquery = {
            '_id'    : {"$in":ptaskIds},
            'status' : {"$in":[TASK_STATUS_COMPUTED]}
        }
        ptasks = self.getModels('PTask',pquery,100)

        obj.finishedPtask = [task['_id'] for task in ptasks] 


class AluCheckAli(Alu):
    '''检查Ali 
    '''

    def __init__(self,aliId):
        self.aluType = 'CheckAli'
        super(AluCheckAli, self).__init__()

        self.aliId = aliId

    def run(self,obj):
        ''' 检查所有的follower是否有效 如果无效重新分派任务
        '''
        
        while True:
            
            #判断是非为Leader 如果不是sleep 
            if obj.aliType != ALI_TYPE_LEADER:
                gevent.sleep(SLEEP_NOT_LEADER)
                #print "AluCheckAli not leader sleep 10s"
                continue

            query = {
                'status' : ALI_STATUS_NORMAL,
                'aliType': ALI_TYPE_FOLLOWER
                }
            followers_pre = self._list2dict(self.getModels('Ali',query,100))
            
            #睡眠10s 
            gevent.sleep(SLEEP_CHECK_ALI)
            followers_next = self._list2dict(self.getModels('Ali',query,100))

            for ali_id in followers_next:
                if followers_next[ali_id]==followers_pre.get(ali_id,0):
                    print "AluCheckAli check %s abnormal" % ali_id
                    self.updateModel('Ali',{'_id':ali_id},{'status':ALI_STATUS_ABNORMAL})

                    #重新分派任务
                    print "AluCheckAli reallot task"
                    updateCond = {'aliId':ali_id,
                            'status':{"$in":[TASK_STATUS_ALLOTED,TASK_STATUS_COMPUTING]}}
                    self.updateModel('TaskQuere',updateCond,{'status':TASK_STATUS_SPLITED})


            followers_pre = None
            followers_next = None

    def _list2dict(self,followers):
        aliDatas = {}
        for ali in followers:
            aliDatas[ali['aliId']] = ali.get('beat',0)
        return aliDatas

class AluCheckTask(Alu):
    '''检查任务 
    '''

    def __init__(self,aliId):
        self.aluType = 'CheckTask'
        super(AluCheckTask, self).__init__()

        self.aliId = aliId

    def run(self,obj):
        ''' 检查任务
            已经分派但实例异常的任务需要重新分派
        '''
        
        while True:
            
            #判断是非为Leader 如果不是sleep 
            if obj.aliType != ALI_TYPE_LEADER:
                gevent.sleep(SLEEP_NOT_LEADER)
                #print "AluCheckTask not leader sleep 10s"
                continue

            query = {
                     'status' : TASK_STATUS_ALLOTED 
                }

            allotedTasks = self.getModels('TaskQuere',query,100)

            for task in allotedTasks:
                ali = self.getModel('Ali',task['aliId'])
                if ali['status'] == ALI_STATUS_ABNORMAL:
                    self.updateModel('TaskQuere',{'_id':task['taskId']},{'status':TASK_STATUS_SPLITED})

                    print "AluCheckTask %s realloted"%task['taskId']

            #1分钟检查一次
            gevent.sleep(SLEEP_CHECK_TASK)
 

      


 

 
