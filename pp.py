from pymongo import MongoClient
import time, logging, pika, re, datetime, threading, json, os


# Log object
logging.basicConfig(filename='/var/log/pp.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.info('container started')

mongo_host = os.environ['mongo']
# mongo client
db_connection = MongoClient(mongo_host)
db = db_connection.cryptocurrency
collection = db.bitcoinprice

settings = {'interval' : 300}
stop_thread = False

def format_date(date):
    ts = datetime.datetime.fromtimestamp(date).strftime('%m/%d %H:%M:%S')
    return ts

def format_text(data):
    max_spot_price, max_buy_price, max_sell_price = get_max_price(data)
    min_spot_price, min_buy_price, min_sell_price = get_min_price(data)
    _text = """
    Bitcoin
    Max Spot Price: %s, date: %s;
    Max Buy Price:  %s, date: %s;
    Max Sell Price: %s, date: %s;
    ----
    Min Spot Price: %s, date: %s;
    Min Buy Price:  %s, date: %s;
    Min Sell price: %s, date: %s;
    """ %(max_spot_price['bitcoin spot price'], format_date(max_spot_price['date']), max_buy_price['bitcoin buy price'], format_date(max_buy_price['date']),
        max_sell_price['bitcoin sell price'], format_date(max_sell_price['date']), min_spot_price['bitcoin spot price'], format_date(min_spot_price['date']),
        min_buy_price['bitcoin buy price'], format_date(min_buy_price['date']), min_sell_price['bitcoin sell price'], format_date(min_sell_price['date']))
    return _text

def max_price(data, k):
    return max(data, key=lambda x: x[k])

def min_price(data, k):
    return min(data, key=lambda x: x[k])

def get_max_price(data):
    max_spot_price = max_price(data,'bitcoin spot price')
    max_buy_price = max_price(data,'bitcoin buy price')
    max_sell_price = max_price(data,'bitcoin sell price')
    return max_spot_price, max_buy_price, max_sell_price

def get_min_price(data):
    min_spot_price = min_price(data,'bitcoin spot price')
    min_buy_price = min_price(data,'bitcoin buy price')
    min_sell_price = min_price(data,'bitcoin sell price')
    return min_spot_price, min_buy_price, min_sell_price

threads = []

# thread creator
def thread_func(collection, settings):
    logging.info("starting thread function")
    t = threading.Thread(name='btc_price',target=btc_price, args=(collection, settings, lambda : stop_thread))
    threads.append(t)
    t.start()
    while True:
        logging.info("thread status: %s" %str(t.isAlive()))
        time.sleep(10)

def pika_publisher(queue_name, host, message):
    logging.info("[x] Sent %r" % message)
    connection_reply = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel_reply = connection_reply.channel()
    channel_reply.queue_declare(queue=queue_name)
    channel_reply.basic_publish(exchange='',
                          routing_key='bot_send',
                          body=json.dumps(message))
    connection_reply.close()

def btc_price(collection, settings, stop):
    try:
        while True:
            current_epoch_time = time.time()
            start_time = current_epoch_time - settings['interval']
            query = {'date': {'$gt': start_time, '$lt': current_epoch_time}} 
            data = collection.find(query)
            list_of_data = []
            for i in data: list_of_data.append(i)
            if list_of_data:
                text = format_text(list_of_data)
                message = {'kind' : 'send_msg', 'message': text}
                logging.info(text)
                pika_publisher('bot_send', rabbit_host, message)
            else:
                logging.info('no data from query')
            if stop():
                logging.info('restarting btc_price')
                break
        except Exception as e:
            logging.info("exception: %s" %e)
        logging.info('sleeping %s' %settings['interval'])
        time.sleep(settings['interval'])


def callback(ch, method, properties, body):
    body = json.loads(body)
    if body['settings']:
        global stop_thread
        stop_thread = True
        settings = {**settings, **body['settings']}
        thread_func(collection,settings)
    logging.info("[x] Received %r" % body)

# call initial thread
thread_func(collection,settings)

# init Rabbitmq queue and listen for commands.
rabbit_host = os.environ['rabbit']
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
channel = connection.channel()
channel.queue_declare(queue='pp')    # deployer queue for actions to send msg to bot
channel.basic_consume('pp', callback)
logging.info('consumer started. listening on bot send channel..')
channel.start_consuming()
