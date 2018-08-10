from qlib.data import dbobj, Cache
from concurrent.futures.thread import  ThreadPoolExecutor
from termcolor import colored
import importlib

import tornado
import base64
import pickle
import json
import os
import sys

TEST_MODULES_ROOT = os.path.expanduser("~/.config/SwordNode/plugins/Plugins")
REPO_DB = os.path.expanduser("~/.config/SwordNode/plugins/repo.db")
DEFAULT_REPO_PATH = os.path.expanduser("~/.config/SwordNode/plugins/Plugins")
REPO_NOW_USE = os.path.expanduser("~/.config/SwordNode/plugins/now_repo")

class OO:pass

class Repo(dbobj):pass

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

    def set_repo(self, name,url, path):
        c = Cache(REPO_DB)
        if path.endswith("/"):
            path = path[:-1]
        r = Repo(name=name, url=url, path=path)
        os.popen("cd %s && git init || git remote add %s  %s" % (r.path.strip(), r.name.strip(), r.url.strip()))
        r.save(c)

    def update(self, repo_name):
        c = Cache(REPO_DB)
        r = c.query_one(Repo, name=repo_name)
        if not r:
            r = c.query_one(Repo)
        
        if r:
            return os.popen("cd %s && pwd &&  git fetch --all && git reset --hard %s/master && sleep 1 && ls" % (r.path.strip(), r.name)).read()
        else:
            self.set_repo('origin', 'https://github.com/Qingluan/x-plugins.git', TEST_MODULES_ROOT)
            res = self.update(repo_name)
            return "rebuild... " + res

    def switch_repo(self, repo_name):
        c = Cache(REPO_DB)
        r = c.query_one(Repo, name=repo_name)
        with open(REPO_NOW_USE, 'w') as fp:
            fp.write(r.path.strip())
    
    def use_repo(self):
        if os.path.exists(REPO_NOW_USE):
            with open(REPO_NOW_USE) as fp:
                N = fp.read()
                dname = os.path.dirname(N)
                mname = os.path.basename(N)
                if dname not in sys.path:
                    sys.path += [dname]
                return mname
        else:
            dname = os.path.dirname(TEST_MODULES_ROOT)
            mname = os.path.basename(TEST_MODULES_ROOT)
            if dname not in sys.path:
                sys.path += [dname]
            return mname


    def cat(self, file):
        c = Cache(REPO_DB)
        r = c.query_one(Repo, name=self.use_repo())
        if r:
            files = os.listdir(r.path)
            for f in fils:
                if file in f:
                    with open(os.path.join(r.path, f)) as fp:
                        return fp.read()
            return "no file: %s" % file
        return "no current repo"


    def load(self, name):
        mname = self.use_repo()
        try:
            return importlib.import_module("%s.%s" % (mname, name))
        except ModuleNotFoundError as e:
            files = os.listdir(TEST_MODULES_ROOT)
            if (name + ".bash") in files:
                def _run(*args, **kargs):
                    res = os.popen('bash %s {}'.format(" ".join(['"%s"' % i for i in args])) % os.path.join(TEST_MODULES_ROOT, name + ".bash")).read()
                    return res
                OO.run = _run
                return OO
            return str(e)
        

    def run(self, *args, **kargs):
        if self.name == 'self':
            if len(args) == 1 and args[0]:

                wargs = args[0].split(",")
                if len(wargs) ==3:
                    name = ''
                    path = ''
                    url = ''
                    for i in wargs:

                        if 'https://github' in  i:
                            url = i.strip()
                            continue
                        elif '/' in i:
                            path = i
                            if not os.path.exists(path):
                                try:
                                    os.mkdir(path)
                                except Exception as e:
                                    return path + " Not found"
                            continue

                        name = i

                    self.set_repo(name, url, path)
                    return "repo set : name=%s url=%s path=%s " % (name, url, path)
                elif len(wargs) == 2 and wargs[0] == 'use':
                    self.switch_repo(wargs[1].strip())
                    return 'switch to : %s' % wargs[1]
                elif wargs[0] == 'ls':
                    c = Cache(REPO_DB)
                    rs = c.query(Repo)
                    return json.dumps([r.get_dict() for r in rs])
                elif len(wargs) ==2 and wargs[0] == 'cat':
                    
                    return self.cat(wargs[1])
                else:
                    c = Cache(REPO_DB)
                    r = c.query_one(Repo, name=wargs[0])
                    if r:
                        res = self.update(r.name)
                        return res
                    return """suport:
                    Was sagst du? %s 
                        curl http://xxxx -d module=self -d args=ls # ls all repo
                        curl http://xxxx -d module=self -d args=help
                        curl http://xxxx -d module=self -d args=name,url,path # set repo
                        curl http://xxxx -d module=self -d args=use,origin  # switch repo
                        curl http://xxxx -d module=self  # this will update use now repo

                    """ % wargs
                
            else:
                res = self.update("")
                return res
        else:
            Obj = self.load(self.name)
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
            keys = self.handle.request.arguments
            
        tp = extr('type')
        args = extr('args')
        self.module = extr('module')
        self.type = tp
        self.kwargs = {}
        for k in keys:
            if k in ['type', 'args', 'module']:
                continue
            self.kwargs[k] = extr(k)

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
