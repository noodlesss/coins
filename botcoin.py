import os, json, time, logging, requests, pika
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)
from config import *

# Log object
logging.basicConfig(filename='main_ctr.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.info('container started')

# Rabbitmq reply queue callback
# called when received a message from reply queue. results of tasks.
def reply_queue_callback(ch, method, properties, body):
    body = json.loads(body)
    logging.info('[x] bot: %s' %body)
    if body['kind'] == 'send_msg':
        bot.sendMessage(chat_id, body['message'])


# Telegram handler
def handler(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    pass

def bot_callback(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    pass

# bot listener
logging.info('Token: %s' %token)
#initialize bot
bot = telepot.Bot(token)
MessageLoop(bot, {'chat': handler,
                  'callback_query': bot_callback}).run_as_thread()
logging.info('bot started listening')
bot.sendMessage(chat_id, 'ellie started')


# rabbitmq listener

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel_reply = connection.channel()
channel_reply.queue_declare(queue='bot_send')
channel_reply.basic_consume(reply_queue_callback, queue='bot_send', no_ack=True)
logging.info('consumer started. listening..')
channel_reply.start_consuming()

