import os, sys, socks, json
from qlib.data import dbobj, Cache
from base64 import b64encode, b64decode
from functools import partial
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import  MessageMediaDocument
from telethon.utils import get_display_name
import logging
import asyncio

USER_DB_PATH = os.path.expanduser("~/.config/SwordNode/user/.tel.sql")

if not os.path.exists(os.path.dirname(USER_DB_PATH)):
    os.mkdir(os.path.dirname(USER_DB_PATH))


class Token(dbobj):

    async def connect(self, proxy=None, loop=None):
        api_id, api_hash = self.token.split(":")
        api_id = int(api_id)
        client = TelegramClient('session', api_id=api_id, api_hash=api_hash, proxy=proxy)
        client.connect()
        return client
        

    async def send_code(self, client=None, db=None, proxy=None, loop=None):
        if not client:
            client = await self.connect(proxy, loop=loop)
        if not db:
            db = Cache(USER_DB_PATH)
        client.sign_in(phone=self.phone)
        self.hash_code = client._phone_code_hash.get(self.phone[1:])
        self.save(db)

    async def login(self, code, client=None, db=None, proxy=None,loop=None):
        # Ensure you're authorized
        if not client:
            client = await self.connect(proxy, loop=loop)
        if not db:
            db = Cache(USER_DB_PATH)
        if not client.is_user_authorized():
            try:
                client.sign_in(phone=self.phone, code=code, phone_code_hash=self.hash_code)
            except ValueError:
                await self.send_code(client)
                return 'auth fail resend code to your device'
        me = await client.get_me()
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

    def __init__(self, db, proxy=None, loop=None):
        if isinstance(db, str):
            self.db = Cache(db)
        else:
            self.db = db
        self.proxy = proxy
        self.loop = loop

    def registe(self, phone, token, client=None):
        Token.set_token(token, phone, client=client)

    def sendcode(self, phone):
        user = self.db.query_one(Token, phone=phone)
        if user:
            f = asyncio.ensure_future(user.send_code(proxy=self.proxy, loop=self.loop))
            # asyncio.get_event_loop().run_until_complete(f)
            f.add_done_callback(logging.info)

    def login(self, phone, code):
        user = self.db.query_one(Token, phone=phone)
        if user:
            f = asyncio.ensure_future(user.login(code, proxy=self.proxy, loop=self.loop))
            f.add_done_callback(logging.info)
            logging.info(w)
            # = asyncio.get_event_loop().run_until_complete(f)
            # if msg == 'ok':
            return user.hash_code
            # return False
        else:
            return False


    def if_auth(self, hash_code):
        user = self.db.query_one(Token, hash_code=hash_code)
        if user:
            return True
        return False

