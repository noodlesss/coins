from coinbase.wallet.client import Client
from pymongo import MongoClient
import time, logging, pika, re, datetime, os

# Log object
try:
    logging.basicConfig(filename='/var/log/dbwriter.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
except Exception as e:
    logging.basicConfig(filename='dbwriter.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.info('container started')


# initialise coinbase client
c = Client('1','2')

coin_list = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR']

# mongo client
mongo_host = os.environ['mongosvc'].rstrip()
db_connection = MongoClient(mongo_host)
db = db_connection.cryptocurrency
#collection = db.coinprice


def coinprice(c, db, coin_list):
  for coin in coin_list:
      collection = db[coin]
      spot_price = c.get_spot_price(currency_pair = coin)
      buy_price = c.get_buy_price(currency_pair = coin)
      sell_price = c.get_sell_price(currency_pair = coin)
      post = {
              '%s spot price' %coin: spot_price['amount'],
              '%s buy price' %coin: buy_price['amount'],
              '%s sell price' %coin: sell_price['amount'],
              'date': time.time()
              }
      logging.info('post: %s' %post)
      collection.insert_one(post)




while True:
  #logging.debug('BTC price at %s: %s' %(time.time(),a['amount']))
  coinprice(c, db, coin_list)
  logging.debug('loop complete')
  time.sleep(60)




