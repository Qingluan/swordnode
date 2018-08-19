from mroylib.api import BaseApi, BaseArgs
from mroylib.config import Config
import tornado
import base64
import pickle
import json
import os
import sys
import logging


config = Config(name='swordnode.ini')
config.section = 'log'

logging.basicConfig(level=getattr(logging, config['level'], 'INFO'))
config.section = 'base'

class TornadoApi(BaseApi):
    BASE_REPO = config['base-repo']
    BASE_DIR =  cofnig['plugin-path']
    
    def callback(self, result):
        tloop = self.loop
        if not tloop:
            tloop = tornado.ioloop.IOLoop.instance()
        
        callback = self.get_callback()
        tloop.add_callback(lambda: callback(result.result()))


class TornadoArgs(BaseArgs):

    def get_parameter(self, key, l=None):
        if l == 'head':
            return self.handle.request.headers.get(key)
        else:
            try:
                return self.handle.get_argument(key)
            except Exception as e:
                return None
      

    def get_parameter_keys(self):
        return self.handle.request.arguments

    def finish(self, data):
        self.handle.write(data)
        self.handle.finish()
    
