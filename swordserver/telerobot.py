# -*- coding: utf8 -*-
from qlib.data import Cache,dbobj
from qlib.net import to
from qlib.io import GeneratorApi
from mroylib.auth import Token

from functools import partial
import urllib.parse as up
import json
import os
import logging
import time

logging.basicConfig(level=logging.INFO)

class Bot(dbobj):
    pass
class OO:
    def __init__(self):
        self.msg_text = ""


def get_my_ip():
    res = to("http://ipecho.net/plain").text.strip()
    return res

class Message(dbobj):

    
    def get_chat(self):
        return json.loads(self.to_chat)
    

    def to_msg(self,token, msg):
        base = 'https://api.telegram.org/bot%s/' % token
        url = up.urljoin(base, 'sendMessage')
        chat = self.get_chat()
        url += "?" + up.urlencode({'chat_id':chat['id'], 'text':msg})
        res = to(url).json()
        return res['ok']
        
    @classmethod
    def update_msg(cls, token):
        base = 'https://api.telegram.org/bot%s/' % token
        url = up.urljoin(base, 'getUpdates')
        logging.info(f"update url:{url}")
        res = to(url).json()
        if res['ok']:
            for m in res['result']:
                mm = m['message']
                yield cls(msg_id=mm['message_id'], msg_text=mm['text'],to_chat=json.dumps(mm['chat']), from_chat=json.dumps(mm['from']), time=mm['date'], update_id=m['update_id'])

    @staticmethod
    def new(path):
        c = Cache(path)
        try:
            f = max(c.query(Message), key=lambda x: x.id)
            return f
        except ValueError:
            return None


def update_auth(db,token):
    c = Cache(db)
    t = c.query_one(phone='0')
    if not t:
        t = Token(tp='tel', token='0', phone='0', hash_code=token, set_timeout=24*60)
    t.hash_code = token
    
    res = t.save(c)
    logging.info(f"db handle : {res}")

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

class  TokenTel(object):
    """docstring for  TokenTel"""
    def __init__(self, token, db, interval=10):
        self.token = token
        self.db = db
        self._map = {}
        self.interval = interval
        
    def get_command(self, msg_text):
        if msg_text.startswith('/'):
            token = msg_text.split()
            return token[0][1:],token[1:]
        return '',''
    
    def reg_callback(self, com, function):
        self._map[com] = function

    def run(self):
        db = Cache(self.db)
        print(f"connect to db: {self.db}")
        while 1:
            msgs = list(Message.update_msg(self.token))
            
            new_msg = None
            for msg in msgs:
                if db.query_one(Message, msg_id=msg.msg_id):continue
                msg.save(db)
                print(f"to db : {msg.msg_id} : {msg.time}", end='\r')
                new_msg = msg

            
            if new_msg:
                print(f"got new: {new_msg.msg_id} => {new_msg.msg_text}")
                com, args = self.get_command(new_msg.msg_text)
                f = self._map.get(com)
                if f:
                    print(f"callback {com} : {args}")
                    try:
                        f(*args)
                    except Exception as e:
                        logging.info(str(e))
                        print(f"err {str(e)}")
            time.sleep(self.interval)
            

def reg(auth_db, token, x):
    update_auth(auth_db, x)
    print("run reg")
    Message.new(auth_db).to_msg(token, get_my_ip() + " reg : %s" % x)
        
def run_other_auth(token, auth_db):
    t = TokenTel(token, auth_db)
    t.reg_callback('reg', lambda x: partial(auth_db, token)(x))
    t.reg_callback('check', lambda : Message.new(auth_db).to_msg(token, get_my_ip() + " √"))
    t.run()

def main():
    args = GeneratorApi({
        'token': "set token",
        'db': 'set db path',
    })
    if args.token and args.db:
        if os.path.exists(args.db):
            run_other_auth(args.token, args.db)

