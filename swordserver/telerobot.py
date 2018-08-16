import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler,Filters
from telegram.ext import Updater
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater
from telegram.ext import InlineQueryHandler, ChosenInlineResultHandler


# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


updater = Updater(token='685928995:AAFwz7cns6ziGgkecbqhJ2JpLtcO8tur-HA')
dispatcher = updater.dispatcher


def command(handler,cmd=None,**kw):
    def decorater(func):
        def wrapper(*args,**kw):
            return func(*args,**kw)
        if cmd==None:
            func_hander=handler(func,**kw)
        else:
            func_hander=handler(cmd,func,**kw)
        dispatcher.add_handler(func_hander)
        return wrapper
    return decorater

@command(CommandHandler, 'echo', pass_args=True)
def echo(bot,update,args):
    text_caps=' '.join(args).upper()
    print(args)
    bot.sendMessage(chat_id=update.message.chat_id,text=text_caps)


@command(MessageHandler, Filters.text)
def get_message(bot,update,args):
    text_caps=' '.join(args).upper()
    print(args, update.message)

@command(MessageHandler,Filters.text)
def unknown(update,bot):
    print(update.message.text)
    bot.sendMessage(chat_id=update.message.chat_id,text="Sorry, I didn't understand that command.")


    # bot.sendMessage(chat_id=update.message.chat_id,text=text_caps)

# def inline_caps(bot, update):
#     logging.debug('HI')
#     query = update.inline_query.query
#     if not query:
#         return
#     results = list()
#     results.append(
#         InlineQueryResultArticle(
#             id=query.upper(),
#             title='Caps',
#             input_message_content=InputTextMessageContent(query.upper())
#             )
#         )
#     bot.answerInlineQuery(update.inline_query.id, results)

# def say_hello(bot, update):
#     print('HELLO')
#     print(update.to_dict())


updater.start_polling()
# updater.idle()
# updater.stop()