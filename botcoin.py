import os, json, time, logging, requests, pika
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)


# Log object
try:
    logging.basicConfig(filename='/var/log/bot.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
except Exception as e:
    logging.basicConfig(filename='bot.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

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



#initialize bot
token = os.environ['token']
chat_id = os.environ['chatid']
bot = telepot.Bot(token)
# bot listener
logging.info('Token: %s' %token)
logging.info('chat id: %s' %chat_id)
MessageLoop(bot, {'chat': handler,
                  'callback_query': bot_callback}).run_as_thread()
logging.info('bot started listening')
try: 
    bot.sendMessage(chat_id, 'ellie started')
except Exception as e:
    logging.info(e)


# rabbitmq listener
rabbit_host = os.environ['rabbitsvc']
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
channel_reply = connection.channel()
channel_reply.queue_declare(queue='bot_send')
channel_reply.basic_consume('bot_send', reply_queue_callback)
logging.info('consumer started. listening..')
channel_reply.start_consuming()

