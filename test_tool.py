from cmd import Cmd
import requests
from termcolor import colored
import json
import sys


def l(*args, tp='son',**kargs):
    if tp == 'json':
        data = args[0]
        s = json.loads(data)
        print(colored("[+]",'green'), s['res'])
    else:   
        print(colored("[+]",'green'), *args, **kargs)


class TestCmd(Cmd):

    def __init__(self, url):
        super().__init__()
        self.prompt = colored("(Ja, so ist es):", 'green')
        self.module = 'self'
        self.args = None
        self.url = url


    def do_set_module(self, args):
        self.module = args
        l(self.module, tp=None)

    def do_args(self, args):
        if not args:
            res = requests.post(self.url, data={
                'module':self.module,
            }).json()
            if 'res' in res:
                res = res['res']
            elif 'error' in res:
                res = res['error']
            l(res)
        else:
            res = requests.post(self.url, data={
                'module':self.module,
                'args':args
            }).json()
            if 'res' in res:
                res = res['res']
            elif 'error' in res:
                res = res['error']
            l(res)




if __name__ == '__main__':
    t = TestCmd(sys.argv[1])
    t.cmdloop()