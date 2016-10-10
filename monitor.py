#!/usr/bin/env python
# encoding=utf8

''' 监控模块
'''

import time
from model import Model
from prettytable import PrettyTable
from colorama import init,Fore

import sys
import os
from argparse import ArgumentParser


class EdcMonitor(object):
    ''' 监控模块   
    '''

    def __init__(self):
        self.count = 0
        pass

    def run(self):
        '''执行
        '''
        lstAli,lstTask,lstLog = self._getData()

        self._show(lstAli,lstTask,lstLog)


    def _getData(self):
        '''获取数据
        '''
        model = Model()

        #实例数据
        lstAli = model.getModels('Ali',{},10,[('addtime', -1)])

        #任务数据
        lstPTask = model.getModels('PTask',{},10,[('addtime', -1)])
        lstTask = []
        for task in lstPTask:
            ptaskId = task['_id']
            lstTask.append(
                    {
                        '_id'     : task['_id'],
                        'bizType' : task['bizType'],
                        'status'  : task['status'],
                        'stTotal' : model.getCount('TaskQuere',{'PTaskId':ptaskId}),
                        'stRun'   : model.getCount('TaskQuere',{'PTaskId':ptaskId,'status':'computing'}),
                        'stAllot' : model.getCount('TaskQuere',{'PTaskId':ptaskId,'status':'alloted'}),
                        'stSpilt' : model.getCount('TaskQuere',{'PTaskId':ptaskId,'status':'splited'}),
                        'stFail'  : model.getCount('TaskQuere',{'PTaskId':ptaskId,'status':'failed'}),
                        'stComputed' : model.getCount('TaskQuere',{'PTaskId':ptaskId,'status':'computed'}),
                    }
            )
        
        #查询日志
        lstLog = model.getModels('Logger',{},10)

        return lstAli,lstTask,lstLog


    def _show(self,lstAli,lstTask,lstLog):
        '''显示
        '''

        
        ptAli = PrettyTable(["实例", "类型","状态","Ip","Host","Cpu","Mem","线程数","运行数","❤️ 次数"])
        for ali in lstAli:

            status = ali['status']
            if status=='abnormal' : 
                status = self._red(status) 

            aliType = ali['aliType']
            if aliType=='Leader' : 
                aliType = self._red(aliType) 

            ptAli.add_row([ali['_id'][:8],
                aliType,
                status,
                ali['ip'],
                ali.get('hostname',''),
                ali['cpu'],
                ali['mem'],
                ali['thNum'],
                ali['runCount'],
                ali['beat']
            ])
   
        ptAli.sort_key("类型")
        ptAli.reversesort = True
 

        ptTask = PrettyTable(["任务", "类型","状态","ST总数","ST计算","ST分派","ST未执行","ST失败","ST完成"])
        for task in lstTask:

            status = task['status']
            if status=='failed' : 
                status = self._red(status) 

            ptTask.add_row([
                task['_id'][:8],
                task['bizType'],
                status,
                task['stTotal'],
                task['stRun'],
                task['stAllot'],
                task['stSpilt'],
                task['stFail'],
                task['stComputed']
            ])
   
        ptTask.sort_key("类型")
        ptTask.reversesort = True
         
        ptLog = PrettyTable(["操作", "类型","实例","任务","日志内容","时间"])
        init(autoreset=True)

        for log in lstLog:
 
            logType = log['logType']
            if log['logType']=='error' : 
                logType = self._red(log['logType']) 
            if log['logType']=='warn' : 
                logType = self._yellow(log['logType']) 

            ptLog.add_row([
                log['opName'],
                logType,
                log['aliId'][:8],
                log['ptaskId'][:8],
                log['logContent'],
                log['addtime'] 
            ])
   
        ptLog.sort_key("类型")
        ptLog.reversesort = True


        os.system("clear")
        print "实例信息"
        print(ptAli)

        print "任务信息"

        print(ptTask)

        print "执行日志"
        print(ptLog)

        print "\n"
        print "\33[5m\r❤️ %d\033[0m" % self.count


    def _red(self, s):
        return Fore.RED + s + Fore.RESET
    
    def _yellow(self, s):
        return Fore.YELLOW + s + Fore.RESET  


def getArguments():
    """Get command line arguments
    """
    parser = ArgumentParser(description = "Edc监控 "\
     " eg: ./monitor.py --tick 3")
     
    parser.add_argument('--tick', dest = 'tick', help = 'timed execution eg. 10')
 
    # Done
    return parser.parse_args()

if __name__ == '__main__':

    args = getArguments()

    tick = args.tick
    if tick:
        tick = int(tick)

    monitor = EdcMonitor()

    while tick > 0:
        monitor.count+=1
        monitor.run()
        time.sleep(tick)

    monitor.run()

    

   

