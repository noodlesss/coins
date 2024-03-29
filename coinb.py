from coinbase.wallet.client import Client
from pymongo import MongoClient
import time, logging, pika, re, datetime, os

# Log object
try:
    logging.basicConfig(filename='/var/log/coinb.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
except Exception as e:
    logging.basicConfig(filename='coinb.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.info('container started')


# initialise coinbase client
c = Client('1','2')


# mongo client
mongo_host = os.environ['mongosvc'].rstrip()
db_connection = MongoClient(mongo_host)
db = db_connection.cryptocurrency
collection = db.bitcoinprice

while True:
  spot_price = c.get_spot_price(currency_pair = 'BTC-EUR')
  buy_price = c.get_buy_price(currency_pair = 'BTC-EUR')
  sell_price = c.get_sell_price(currency_pair = 'BTC-EUR')
  #logging.debug('BTC price at %s: %s' %(time.time(),a['amount']))
  post = {
          'BTC-EUR spot price': int(float(spot_price['amount'])),
          'BTC-EUR buy price': int(float(buy_price['amount'])),
          'BTC-EUR sell price': int(float(sell_price['amount'])),
          'date': time.time()
          }
  collection.insert_one(post)
  logging.debug('loop complete')
  time.sleep(60)




