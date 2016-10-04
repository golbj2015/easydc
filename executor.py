# encoding=utf8
# The task base
import gevent

class TaskExecutor(object):
 
    def __call__(self, task):
        
        raise NotImplementedError


class EchoTaskExecutor(TaskExecutor):

    id = 'edc.echo'
    def __call__(self,opType, task):

        print "EchoTaskExecutor start",opType
        #print gevent.getcurrent()
        gevent.sleep(30)

        print "EchoTaskExecutor end"
        return "ok"
 

class AddTaskExecutor(TaskExecutor):

    id = 'edc.add'
    def __call__(self, opType,task):


        print "AddTaskExecutor start",opType
        #print gevent.getcurrent()
        gevent.sleep(30)
        print "AddTaskExecutor end"

        return "ok"
 


EXECUTORS = {
    EchoTaskExecutor,
    AddTaskExecutor

 }