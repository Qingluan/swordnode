from qlib.data import Cache,dbobj
from qlib.net import to
from qlib.io import GeneratorApi
from mroylib.auth import Token

import urllib.parse as up
import json
import os
import logging
import time

class Bot(dbobj):
    pass
class OO:
    def __init__(self):
        self.text = ""


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
                yield cls(id=mm['message_id'], msg_text=mm['text'],to_chat=json.dumps(mm['chat']), from_chat=json.dumps(mm['from']), time=mm['date'], update_id=m['update_id'])

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
    t.save(c)

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
            if len(token) > 1:
                return token[0][1:],token[1:]
        return '',''
    
    def reg_callback(self, com, function):
        self._map[com] = function

    def run(self):
        db = Cache(self.db)
        while 1:
            msgs = Message.update_msg(self.token)
            try:
                n = max(msgs, key=lambda x: x.id)
            except ValueError:
                n = OO()
            com, args = self.get_command(n.text)
            f = self._map.get(com)
            if f:
                f(*args)
            time.sleep(self.interval)
            db.save_all(*msgs)

        
def run_other_auth(token, auth_db):
    t = TokenTel(token, auth_db)
    t.reg_callback('reg', lambda x: update_auth(auth_db, x))
    t.reg_callback('check', lambda x: Message.new(auth_db).to_msg(token, get_my_ip()))
    t.run()

def main():
    args = GeneratorApi({
        'token': "set token",
        'db': 'set db path',
    })
    if args.token and args.db:
        if os.path.exists(args.db):
            run_other_auth(args.token, args.db)

