
#!/usr/bin/python
## write by qingluan 
# just a run file 

import tornado.ioloop
from tornado.ioloop import IOLoop
from .setting import  appication, port
from qlib.io import GeneratorApi
import os
J = os.path.join
HOME = os.path.expanduser("~/.config/SwordNode/")
cak = J(HOME, 'server.key')
cac = J(HOME, 'server.crt')

def main():
    args = GeneratorApi({
        'port':"set port ",
        })
    if args.port:
        port = int(args.port)

    http_server = tornado.httpserver.HTTPServer(appication, ssl_options={
        "certfile": cac,
        "keyfile": cak,
    })
    http_server.listen(443)
    tornado.ioloop.IOLoop.instance().start()
    

if __name__ == "__main__":
    main()
    