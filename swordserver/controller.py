
## this is write by qingluan 
# just a inti handler 
# and a tempalte offer to coder
import json
import tornado
import tornado.web
import socks
from tornado.websocket import WebSocketHandler
from .libs import RApi
from .libs import TornadoArgs
from .auth import Auth

import logging

class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.db = self.settings['db']
        self.L = self.settings['L']
        self.tloop = tornado.ioloop.IOLoop.current()
    def get_current_user(self):
        return (self.get_cookie('user'),self.get_cookie('passwd'))
    def get_current_secure_user(self):
        return (self.get_cookie('user'),self.get_secure_cookie('passwd'))
    def set_current_seccure_user_cookie(self,user,passwd):
        self.set_cookie('user',user)
        self.set_secure_cookie("passwd",passwd)

    def json_reply(self,data):
        self.write(json.dumps(data))


class SocketHandler(WebSocketHandler):
    """ Web socket """
    clients = set()
    con = dict()
         
    @staticmethod
    def send_to_all(msg):
        for con in SocketHandler.clients:
            con.write_message(json.dumps(msg))
         
    @staticmethod
    def send_to_one(msg, id):
        SocketHandler.con[id(self)].write_message(msg)

    def json_reply(self, msg):
        self.write_message(json.dumps(msg))

    def open(self):
        SocketHandler.clients.add(self)
        SocketHandler.con[id(self)] = self
         
    def on_close(self):
        SocketHandler.clients.remove(self)
         
    def on_message(self, msg):
        SocketHandler.send_to_all(msg)



class AuthHandler(BaseHandler):

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        parser = TornadoArgs(self, tp='tornado')
        cmd = parser.get_parameter("cmd")
        phone = parser.get_parameter("phone")
        token = parser.get_parameter("token")
        code = parser.get_parameter("code")
        proxy = parser.get_parameter("proxy")

        auth = Auth(self.settings['user_db_path'])
        if cmd == 'regist':
            auth.registe(phone, token)
            self.json_reply({'msg': 'regist ok'})
        elif cmd == 'login':
            client = await  auth.connect(proxy=proxy)
            api_key = await auth.login(cleint=client,phone, code)
            self.json_reply({'api': api_key})
        elif cmd == 'auth':
            client = await  auth.connect(proxy=proxy)
            await auth.sendcode(client=client,phone)
            self.json_reply({'msg':'please recive code!'})
        self.finish()
    

class IndexHandler(BaseHandler):
    
    def prepare(self):
        super(IndexHandler, self).prepare()
        self.template = "template/index.html"

    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/")

    
    

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        parser = TornadoArgs(self, tp='tornado')
        proxy = parser.get_parameter("proxy")
        key = parser.get_parameter("Api-key", l='head')
        if not key:
            self.json_reply({'error': 'no auth!'})
            self.finish()
        else:
            if proxy:
                h,p = proxy.split(":")
                proxy = (socks.SOCKS5, h, int(p))
            
            auth = Auth(self.settings['user_db_path'], proxy=proxy)
            if auth.if_auth(key):
                r = RApi(name=parser.module, loop=self.tloop, callback=parser.after_dealwith)
                print(parser.args, parser.kwargs)
                res = r.run(*parser.args, **parser.kwargs)
                if res:
                    self.json_reply({'error': res})
                    self.finish()
            else:
                self.json_reply({'error': 'No auth!'})
                self.finish()

    