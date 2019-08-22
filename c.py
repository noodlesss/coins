from coinbase.wallet.client import Client
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)

# Log object
logging.basicConfig(filename='main.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.info('container started')

# initialise coinbase client
c = Client('1','2')

# bot chat handler
def handler(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    logging.info('msg handler: %s' %msg['text'])


token = os.environ['token']
chat_id = '165756165'
logging.info('Token: %s' %token)
#initialize bot
bot = telepot.Bot(token)
MessageLoop(bot, {'chat': handler,
                  'callback_query': bot_callback}).run_as_thread()
logging.info('bot started listening')
bot.sendMessage(chat_id, 'price monitoring started')

# initialise coinbase client
c = Client('1','2')

while True:
  a = c.get_spot_price(currency_pair = 'BTC-EUR')
  #logging.debug('BTC price at %s: %s' %(time.time(),a['amount']))
  cur_price = a['amount']
  if float(cur_price) >= 9830.90:
  	bot.sendMessage(chat_id, 'price is %s' %a['amount'])
  time.sleep(60)
