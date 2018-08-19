
#!/usr/bin/python
## write by qingluan 
# just a run file 

import tornado.ioloop
from tornado.ioloop import IOLoop
from .setting import  appication, port
from qlib.io import GeneratorApi
import os
import ssl
from mroylib.config import Config
J = os.path.join


config = Config(name='swordnode.ini')
config.section = "ssl"
cak = config['keyfile']
cac = config['certfile']



def main():
    args = GeneratorApi({
        'port':"set port ",
        })
    if args.port:
        port = int(args.port)
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(cac,keyfile=cak, password='hello')
    http_server = tornado.httpserver.HTTPServer(appication, ssl_options=ssl_ctx)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
    

if __name__ == "__main__":
    main()
    