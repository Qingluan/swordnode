import os, sys, socks, json
from qlib.data import dbobj, Cache
from base64 import b64encode, b64decode

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import  MessageMediaDocument
from telethon.utils import get_display_name
import logging

from swordserver.setting import USER_DB_PATH

if not os.path.exists(os.path.dirname(USER_DB_PATH)):
    os.mkdir(os.path.dirname(USER_DB_PATH))


class Token(dbobj):

    def connect(self, proxy=None):
        api_id, api_hash = self.token.split(":")
        api_id = int(api_id)
        client = TelegramClient('session', api_id=api_id, api_hash=api_hash, proxy=proxy)
        client.connect()
        return client
        

    def send_code(self, client=None, db=None, proxy=None):
        if not client:
            client = self.connect(proxy)
        if not db:
            db = Cache(DB_PATH)
        client.sign_in(phone=self.phone)
        self.hash_code = client._phone_code_hash.get(self.phone[1:])
        self.save(db)

    def login(self, code, client=None, db=None, proxy=None):
        # Ensure you're authorized
        if not client:
            client = self.connect(proxy)
        if not db:
            db = Cache(USER_DB_PATH)
        if not client.is_user_authorized():
            try:
                client.sign_in(phone=self.phone, code=code, phone_code_hash=self.hash_code)
            except ValueError:
                self.send_code(client)
                return 'auth fail resend code to your device'
        me = client.get_me()
        if me:
            return "ok",client
        return 'fail',client

    @staticmethod
    def set_token(token, phone, client=None):
        c = Cache(USER_DB_PATH)
        if not c.query_one(Token):
            t = Token(tp='tel', token=token, phone=phone, hash_code='0')
            t.save(c)
        else:

            if client and client.is_user_authorized():
                t = Token(tp='tel', token=token, phone=phone, hash_code='0')
                t.save(c)


class Auth:

    def __init__(self, db, proxy=None):
        if isinstance(db, str):
            self.db = Cache(db)
        else:
            self.db = db
        self.proxy = proxy

    def registe(self, phone, token, client=None):
        Token.set_token(token, phone, client=client)

    def sendcode(self, phone):
        user = self.db.query_one(Token, phone=phone)
        if user:
            user.send_code(proxy=self.proxy)

    def login(self, phone, code):
        user = self.db.query_one(Token, phone=phone)
        if user:
            msg,c = user.login(code, proxy=self.proxy)
            if msg == 'ok':
                return user.hash_code
            return False
        else:
            return False


    def if_auth(self, hash_code):
        user = self.db.query_one(Token, hash_code=hash_code)
        if user:
            return True
        return False

