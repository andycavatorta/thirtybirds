"""
peraps go back to passing logging function to other modules
use Queue object to make thread safe
create non-trace decorator for efficiency
how to collect data from other devices?
    all devices send log data to the server


new optional command-line args
    nodename= (overrides local hostname)
    loglevel=trace  ( default is no trace)
    dashboard=true (add role of collecting logs)

internal data formats:
    topic (single word) - defines a flow/shape of data, not its function
    address (path, possibly RESTful) - represents not a final address within the software, but an ontology in the data
    data (hash type) - the payload data

    does the action

"""

###############################################################33

import time
import logging
import inspect
from functools import wraps


class DecoratedMethod(object):

    def __init__(self, func, ignore):
        self.func = func
        self.ignore = ignore

    def __get__(self, obj, cls=None):
        @wraps(self.func) 
        def wrapper(*args, **kwargs):
            if self.func.__name__ not in self.ignore:
                print ">>> Path: %s | Class: %s | Function: %s | Arguments: %s"%(cls.__module__,cls.__name__,self.func.__name__,args)
            #print "before"
            ret = self.func(obj, *args, **kwargs)
            #print "after"
            return ret
        for attr in "__module__", "__name__", "__doc__":
            setattr(wrapper, attr, getattr(self.func, attr))
        return wrapper


class DecoratedClassMethod(object):

    def __init__(self, func, ignore):
        self.func = func
        self.ignore = ignore
        print 'papapapapa', self.ignore

    def __get__(self, obj, cls=None):
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            #print "before"
            ret = self.func(*args, **kwargs)
            #print "+++ Path: %s | Class: %s | Function: %s | Arguments: %s"%(cls.__module__,cls.__name__,self.func.__name__,args)
            #print "after"
            #return ret
        for attr in "__module__", "__name__", "__doc__":
            setattr(wrapper, attr, getattr(self.func, attr))
        return wrapper

def Exception_Collector(ignore=""):
    def _Exception_Collector(cls):
        for name, meth in inspect.getmembers(cls):
            if inspect.ismethod(meth):
                if inspect.isclass(meth.__self__):
                    # meth is a classmethod
                    setattr(cls, name, DecoratedClassMethod(meth,ignore))
                else:
                    # meth is a regular method
                    setattr(cls, name, DecoratedMethod(meth,ignore))
            elif inspect.isfunction(meth):
                # meth is a staticmethod
                setattr(cls, name, DecoratedClassMethod(meth,ignore))
        return cls
    return _Exception_Collector


# class ExceptionCollector_Trace(object):
#     def __init__(self, path, errors = [], errorreturn = None):
#         self.errors = errors
#         self.errorreturn = errorreturn
#         self.path = path

#     def report(self, level, msg, stacktrace=None):
#         print level, self.path, msg, stacktrace

#     def __call__(self, function):
#         def returnfunction(*args, **kwargs):
#             try:
#                 self.report("trace", "starting", None)
#                 return function(*args, **kwargs)
#             except Exception as E:
#                 if type(E) not in self.errors:
#                     raise E
#                 self.report("error", E, traceback.print_exc())
#                 return self.errorreturn
#         return returnfunction

def init(loglevel="quiet"):
    pass
    # # ["trace","info","quiet","silent"]
    # if loglevel == "trace":
    #     return ExceptionCollector_Trace

    # if loglevel == "info":
    #     return ExceptionCollector_Info

    # if loglevel == "quiet":
    #     return ExceptionCollector_Quiet

    # if loglevel == "silent":
    #     return ExceptionCollector_Silent

#ExceptionCollector = ExceptionCollector_Trace

