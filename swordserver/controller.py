
## this is write by qingluan 
# just a inti handler 
# and a tempalte offer to coder
import json
import tornado
import tornado.web
import socks
from tornado.websocket import WebSocketHandler
from .libs import TornadoApi
from .libs import TornadoArgs

from mroylib import auth
from mroylib.auth import Authentication
import logging
import os

_USER_DB_PATH = os.path.expanduser("~/.config/SwordNode/user/.tel.sql")
auth.USER_DB_PATH =  _USER_DB_PATH

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

        _auth = Authentication(self.settings['user_db_path'], loop=self.tloop)
        if cmd == 'regist':
            _auth.registe(phone, token)
            self.json_reply({'msg': 'regist ok'})
            self.finish()
        elif cmd == 'login':
            def _reply(x, client):
                
                self.json_reply({"api": x})
                self.finish()
            _auth.login(phone, code, _reply)
            
        elif cmd == 'auth':
            
            _auth.sendcode(phone)
            self.json_reply({'msg':'please recive code!'})
            self.finish()
        else:
            self.json_reply({"msg":f'error cmd: {cmd}'})
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

        api = TornadoApi(name=parser.module, loop=self.tloop, callback=parser.after_dealwith)
        
        if api.Permission == "auth":
            key = parser.get_parameter("Api-key", l='head')    
            _auth = Authentication(self.settings['user_db_path'], proxy=proxy, loop=self.tloop)
            if _auth.if_auth(key):
                res = api.run(*parser.args, **parser.kwargs)
                if res:
                    self.json_reply({'msg': res})
                    self.finish()
            else:
                self.json_reply({'error': 'No auth!'})
                self.finish()
        else:
            res = api.run(*parser.args, **parser.kwargs)
            if res:
                self.json_reply({'msg': res})
                self.finish()

    