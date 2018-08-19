## write by qingluan 
# this is a config file
# include db and debug , static path 
import os
from os import path
# here to load all controllers
from Qtornado.log import LogControl
from Qtornado.db import *
from .controller import *

# load ui modules
import swordserver.ui as ui
from mroylib.config import Config
import sys
E =  os.path.exists
J = os.path.join
config = Config(name='swordnode.ini')
config.seciton = 'base'

SHOME = config['BASE']


if not E(os.path.expanduser("~/.config/SwordNode/user")):
    os.mkdir(os.path.expanduser("~/.config/SwordNode/user"))

if not E(SHOME):
    os.mkdir(SHOME)

PLUGIN_PATH = config['plugin-path']
if not E(PLUGIN_PATH):
    os.mkdir(os.path.join(SHOME, 'plugins'))
    os.mkdir(os.path.join(PLUGIN_PATH, 'Plugins'))
    with open(J(J(PLUGIN_PATH, 'Plugins'), '__init__.py'), 'w') as fp: pass

sys.path += [PLUGIN_PATH]
DB_PATH = config['user_db']

config.section = 'user'
USER_DB_PATH = config['tel_user_db']

if not E(os.path.dirname(DB_PATH)):
    os.mkdir(os.path.dirname(DB_PATH))

db_connect_cmd = r'database="%s"' % DB_PATH
db_engine = SqlEngine(database=DB_PATH)


# static path 
rdir_path = os.path.dirname(__file__)
static_path = J(rdir_path, "static")
files_path = J(static_path , 'files')
# set log level
LogControl.LOG_LEVEL |= LogControl.OK
LogControl.LOG_LEVEL |= LogControl.INFO

Settings = {
        'db':db_engine,
        'L': LogControl,
        'debug':True,
        "ui_modules": ui,
        "user_db_path":USER_DB_PATH,
        'autoreload':True,
        'cookie_secret':'This string can be any thing you want',
        'static_path' : static_path,
    }


## follow is router
try:
    os.mkdir(files_path)
except FileExistsError:
    pass
#
appication = tornado.web.Application([
                (r'/',IndexHandler),
                (r'/auth',AuthHandler),
                # add some new route to router
                ##<route></route>
                # (r'/main',MainHandler),
         ],**Settings)


# setting port 
port = 8080

