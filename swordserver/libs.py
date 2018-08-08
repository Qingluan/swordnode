from qlib.data import dbobj, Cache
from concurrent.futures.thread import  ThreadPoolExecutor
from termcolor import colored
import importlib

import tornado
import base64
import pickle
import json
import os

TEST_MODULES_ROOT = os.path.expanduser("~/.config/SwordNode/plugins/Plugins")

class OO:pass

def load(name):
    try:
        return importlib.import_module("Plugins.%s" % name)
    except ModuleNotFoundError as e:
        files = os.listdir(TEST_MODULES_ROOT)
        if (name + ".bash") in files:
            def _run(*args, **kargs):
                res = os.popen('bash %s {}'.format(" ".join(['"%s"' % i for i in args])) % os.path.join(TEST_MODULES_ROOT, name + ".bash")).read()
                return res
            OO.run = _run
            return OO
        return str(e)
    


class R:
    exes = ThreadPoolExecutor(max_workers=40)
    def __init__(self, name, loop=None, callback=None):
        self.name = name
        self.loop = loop
        self.__callback = callback

    def run(self, *args, **kargs):
        Obj = load(self.name)
        if isinstance(Obj, str):
            return Obj

        futu = R.exes.submit(Obj.run, *args, **kargs)
        if hasattr(Obj, 'callback'):
            self.__callback = Obj.callback
        futu.add_done_callback(self.callback)

    def _callback(self, r):
        print(colored("[+]",'green'), r)

    def callback(self, result):
        tloop = self.loop
        if not tloop:
            tloop = tornado.ioloop.IOLoop.instance()
        if self.__callback:
            tloop.add_callback(lambda: self.__callback(result.result()))
        else:
            tloop.add_callback(lambda: self._callback(result.result()))




class HandleRest:

    def __init__(self, handle, tp=None):
        self.handle = handle
        self.args = []
        self.kargs = dict()
        self._tp = tp
        self.parse()

    def parse(self):
        if hasattr(self.handle, 'get_argument'):
            def extr(x):
                try:
                    return self.handle.get_argument(x)
                except Exception as e:
                    return None
            
        tp = extr('type')
        args = extr('args')
        self.module = extr('module')
        self.type = tp

        print('rec: %s' % args)

        if tp == 'base64':
            if isinstance(args, str):
                args = args.encode('utf8', 'ignore')
            args = json.loads(base64.b64decode(args))
            if isinstance(args, (list, tuple,)):
                self.args = args
            else:
                self.kargs = args
        elif tp =='json':
            args = json.loads(args)
            if isinstance(args, (list, tuple,)):
                self.args = args
            else:
                self.kargs = args
        else:
            self.args = [args]

    def rest_write(self, data):
        b_data = {'res':None, 'type':'json'}
        if self._tp == 'tornado':
            if isinstance(data, str) or isinstance(data, (list, dict, tuple, )):
                b_data['res'] = data
            elif isinstance(data, (int,float,bool,)):
                b_data['res'] = data
            else:
                b_data['res'] = base64.b64encode(pickle.dumps(data))
                b_data['type'] = 'pickle'

            self.handle.write(json.dumps(b_data))
            self.handle.finish()
        
        else:
            pass
