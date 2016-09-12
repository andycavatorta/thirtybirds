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

class ExceptionCollector_Trace(object):
    def __init__(self, path, errors = [], errorreturn = None):
        self.errors = errors
        self.errorreturn = errorreturn
        self.path = path

    def report(self, level, msg, stacktrace=None):
        print level, self.path, msg, stacktrace

    def __call__(self, function):
        def returnfunction(*args, **kwargs):
            try:
                self.report("trace", "starting", None)
                return function(*args, **kwargs)
            except Exception as E:
                if type(E) not in self.errors:
                    raise E
                self.report("error", E, traceback.print_exc())
                return self.errorreturn
        return returnfunction

class ExceptionCollector_Info(object):
    def __init__(self, path, errors = [], errorreturn = None):
        self.errors = errors
        self.errorreturn = errorreturn
        self.path = path

    def report(self, level, msg, stacktrace=None):
        print level, self.path, msg, stacktrace

    def __call__(self, function):
        def returnfunction(*args, **kwargs):
            try:
                self.report("trace", "starting", None)
                return function(*args, **kwargs)
            except Exception as E:
                if type(E) not in self.errors:
                    raise E
                self.report("error", E, traceback.print_exc())
                return self.errorreturn
        return returnfunction

class ExceptionCollector_Quiet(object):
    def __init__(self, path, collect=False, errors = [], errorreturn = None):
        self.errors = errors
        self.errorreturn = errorreturn
        self.path = path
        self.collect = collect

    def report(self, level, msg, stacktrace=None):
        print level, self.path, msg, stacktrace

    def __call__(self, function):
        def returnfunction(*args, **kwargs):
            try:
                if self.collect:
                    self.report("trace", "starting", None)
                return function(*args, **kwargs)
            except Exception as E:
                if type(E) not in self.errors:
                    raise E
                return self.errorreturn
        return returnfunction

class ExceptionCollector_Silent(object):
    def __init__(self, path, errors = [], errorreturn = None):
        self.errors = errors
        self.errorreturn = errorreturn
        self.path = path

    def report(self, level, msg, stacktrace=None):
        print level, self.path, msg, stacktrace

    def __call__(self, function):
        def returnfunction(*args, **kwargs):
            try:
                self.report("trace", "starting", None)
                return function(*args, **kwargs)
            except Exception as E:
                if type(E) not in self.errors:
                    raise E
                self.report("error", E, traceback.print_exc())
                return self.errorreturn
        return returnfunction

def init(loglevel="quiet"):
    # ["trace","info","quiet","silent"]
    if loglevel == "trace":
        return ExceptionCollector_Trace

    if loglevel == "info":
        return ExceptionCollector_Info

    if loglevel == "quiet":
        return ExceptionCollector_Quiet

    if loglevel == "silent":
        return ExceptionCollector_Silent

ExceptionCollector = ExceptionCollector_Trace

