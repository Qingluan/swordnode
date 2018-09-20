# -*- coding: utf8 -*-
from qlib.data import Cache,dbobj
from qlib.net import to
from qlib.io import GeneratorApi
from mroylib.auth import Token
from mroylib.config import Config
from functools import partial
import urllib.parse as up
import json
import os
import logging
import time
import random
import base64
from hashlib import md5
from shadowsocks_extension import test_route

SEVICES_PATH = os.path.expanduser("~/.config/SwordNode/services")

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

                mg = json.dumps(mm['chat'])
                yield cls(msg_id=mm['message_id'], msg_text=mm['text'],to_chat=mg, from_chat=json.dumps(mm['from']), time=mm['date'], update_id=m['update_id'])

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
    t = c.query_one(Token, phone='0')
    if not t:
        t = Token(tp='tel', token='0', phone='0', hash_code=token, set_timeout=24*60)
    t.hash_code = token
    print(t.hash_code)
    res = t.save(c)
    logging.info(f"db handle : {res}")

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

class  TokenTel(object):

    _my_ip = None
    """docstring for  TokenTel"""

    def __init__(self, token, db, interval=5):
        self.token = token
        self.db = db
        self._map = {}
        self.interval = interval
        if not self._my_ip:
            TokenTel._my_ip = get_my_ip()
            self._my_ip = TokenTel._my_ip

        
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
                # print(f"to db : {msg.msg_id} : {msg.time}", end='\r')
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
            

class Router:

    # @staticmethod
    # def switch_router(auth, token, x):
    #     if 'token ->' in os.popen("x-ea-test -t %s " % x).read():
    #         Message.new(auth).to_msg(token, 'switch vultr ok')

    # @staticmethod
    # def account_info(auth, token):
    #     res = requests.get("https://api.vultr.com/v1/account/info", headers={'API-Key': token}).json()
    #     Message.new(auth).to_msg(token, res)

    @staticmethod
    def config_send(auth_db, token):
        ss_config = {}
        if os.path.exists('/etc/shadowsocks.json'):
            with open('/etc/shadowsocks.json') as fp:
                ss_config = json.load(fp)
        else:
            port = 13000 + random.randint(1, 9)
            passwd = 'thefoolish' + str(port - 13000)
            ss_config = {
                'server':'0.0.0.0',
                'server_port': port,
                'password':passwd,
                'method': 'aes-256-cfb',
            }

        ss_config['server'] = get_my_ip()
        if 'port_password' in ss_config:
            cc = list(ss_config['port_password'].items())
            port,password = cc[random.randint(0, len(cc))]
            ss_config['server_port'] = port
            ss_config['password'] = password
            del ss_config['port_password']

        Message.new(auth_db).to_msg(token, '/ss-config ' + base64.b64encode(json.dumps(ss_config).encode('utf8')).decode('utf8'))

    @staticmethod
    def ss_update(auth_db, token, v_token):
        t = TokenTel(token, auth_db)
        test_route.sync(v_token, my_ip=t._my_ip)
        Message.new(auth_db).to_msg(token, t._my_ip + ":update ok")



    @staticmethod
    def collection_config(auth_db, token, config_str):
        ss = base64.b64decode(config_str.encode('utf8'))
        ip = json.loads(ss.decode('utf8'))['server']
        t = TokenTel(token, auth_db)
        if ip == t._my_ip:
            print("[+]", 'this is my ip.')
            return
        md5_str = md5(ss).hexdigest()
        
        if not os.path.exists(os.path.expanduser("~/.config")):
            os.mkdir(os.path.expanduser("~/.config"))
        
        if not os.path.exists(os.path.expanduser("~/.config/seed")):
            os.mkdir(os.path.expanduser("~/.config/seed"))
        
        if not os.path.exists(os.path.expanduser("~/.config/seed/shadowsocks")):
            os.mkdir(os.path.expanduser("~/.config/seed/shadowsocks"))
        fname = os.path.join(os.path.expanduser("~/.config/seed/shadowsocks"), md5_str + ".json")
        with open(fname, 'w') as fp:
            fp.write(ss.decode('utf8'))

        Message.new(auth_db).to_msg(token, "Collect: %s" % ip)


def reg(auth_db, token, x):
    update_auth(auth_db, x)
    logging.info(f"run reg {x} {auth_db}")
    Message.new(auth_db).to_msg(token, get_my_ip() + " reg : %s" % x)

def list_services(auth_db, token, ip=None):
    t = TokenTel(token, auth_db)
    if ip and ip != t._my_ip:
        print("not my ip:",ip)
        return
    
    res = '\n'.join(os.listdir(SEVICES_PATH))
    Message.new(auth_db).to_msg(token, t._my_ip + ": %s" % res)    

def show_status(auth_db, token, service,ip=None):
    t = TokenTel(token, auth_db)
    if ip and ip != t._my_ip:
        return
    res = os.popen("supervisorctl status %s "% service).read()
    Message.new(auth_db).to_msg(token, t._my_ip + ":\n%s" % res) 


def add_services(auth_db, token, file_b64, ip=None):
    t = TokenTel(token, auth_db)
    if ip and ip != t._my_ip:
        return
    
    
    if file_b64.startswith('http'):
        with open('/tmp/run.sh', 'wb') as fp:
            r = requets.get(file_b64, stream=True)
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: fp.write(chunk)
    else:
        with open('/tmp/run.sh', 'wb') as fp:
            try:
                c = base64.b64decode(file_b64.encode('utf-8'))
                fp.write(c)
            except Exception as e :
                res = str(e)            
                Message.new(auth_db).to_msg(token, t._my_ip + ": %s" % res)
                return 

    res = os.popen('bash /tmp/run.sh').read()
    Message.new(auth_db).to_msg(token, t._my_ip + ": %s" % res)    


def help(auth_db,token):
    doc = """
    you can :
        /reg xxx         # to change server's rpc token.
        /check           # to ping all online server.
        /show            # to ping all online server.
        /ss_update       # to let all server send it self's config.
        /status services #
        /help            # to change vultr account token.
        /list            # list all service in this server.
        /add  [http://xxx/ base64_str] ip
                         # to add file to run bash , you can type file address or file content's base str
    """
    Message.new(auth_db).to_msg(token, doc)
        
def run_other_auth(token, auth_db):

    t = TokenTel(token, auth_db)
    t.reg_callback('reg', lambda x: partial(reg, auth_db, token)(x))
    t.reg_callback('check', lambda : Message.new(auth_db).to_msg(token, t._my_ip + " √"))
    t.reg_callback('update', updater)
    t.reg_callback('ss_update', partial(Router.ss_update, auth_db, token))
    t.reg_callback('show', partial(Router.config_send, auth_db, token))
    t.reg_callback('status', partial(show_status, auth_db, token))
    # t.reg_callback('account', partial(Router.switch_router, auth_db, token))
    t.reg_callback('help', partial(help, auth_db, token))
    t.reg_callback('list', partial(list_services, auth_db, token))
    t.reg_callback('add', partial(add_services, auth_db, token))
    t.run()



def updater(x, *cmds):
    if 'github' in x:
        os.popen('pip3 install -U git+https://github.com/%s.git && %s' % (x ,' '.join(cmds)))
    else:
        os.popen('pip3 uninstall -y %s && pip3 install %s -U --no-cache && %s' % (x, x ,' '.join(cmds)))


def main():
    config = Config(name='swordnode.ini')
    config.section = 'user'
    token = config['token']
    db = config['tel_user_db']
    if token and db:
        if not  os.path.exists(db):
            with open(db ,'w') as fp:pass
        run_other_auth(token, db)

