from mroylib.api import BaseApi, BaseArgs
import tornado
import base64
import pickle
import json
import os
import sys
import logging


logging.basicConfig(level=logging.INFO)

class TornadoApi(BaseApi):
    BASE_REPO = 'https://github.com/Qingluan/x-plugins.git'
    BASE_DIR =  os.path.expanduser("~/.config/SwordNode/plugins")
    
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
    
