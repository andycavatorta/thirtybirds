
class ExceptionCollector(object):
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

