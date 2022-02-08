import websocket, json, pandas as pd, asyncio
from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *
from free_module.save_data import *
from free_module.bot_graph import *
from free_module.bot_tweet import *
from strategy.signal import *
from server.config import *

TRADE_SYMBOL = PAIR.upper()

# WIP : time to cancel order
# EXPIRE = False
# EXPIRE_DATE = 1660

PATH_TRADE = f'data/trade.csv'
PATH_DATA = f'data/data.csv'

# clear data.csv/trade.csv
with open(PATH_DATA, "w") as f: 
    f.write("Date,Open,High,Low,Close,Volume")
with open(PATH_TRADE, "w") as f: 
    f.write("Date,Type,Price,Quantity\n")

# contain id of sell limit order
order_id = 0
in_position = False
# start with a buy
side_buy = True 
s_order_price = 0
last_order = 0

test_price = 0
# init client for binance api
client = Client(API_KEY, API_SECRET, tld='com',testnet=TESTNET)

if TESTNET :
    # use testnet wss
    SOCKET = "wss://testnet.binance.vision/ws/"+PAIR+"@kline_1m"
else:
    SOCKET = "wss://stream.binance.com:9443/ws/"+PAIR+"@kline_1m"

if FUTURE:
    SOCKET = "wss://fstream.binance.com/ws/"+PAIR+"@kline_1m"
    #client.API_URL = 'https://fapi.binance.com'

# place order on binance
def order(limit,side):
    global order_id
    order_id = 0
    try:
        # place limit order
        if FUTURE:
            client.futures_change_leverage(symbol=TRADE_SYMBOL, leverage=FUTURE_LEVERAGE)
            if FUTURE_COIN: # COIN-M wip
                order = client.futures_coin_create_order(
                    symbol=TRADE_SYMBOL,
                    side=side,
                    type=FUTURE_ORDER_TYPE_LIMIT,
                    quantity=QUANTITY,
                    price=limit,
                    timeInForce=TIME_IN_FORCE_GTC)
            else: # USD-M
                order = client.futures_create_order(
                    symbol=TRADE_SYMBOL,
                    side=side,
                    type=FUTURE_ORDER_TYPE_LIMIT,
                    quantity=QUANTITY,
                    price=limit,
                    timeInForce=TIME_IN_FORCE_GTC)
        else: # SPOT BUY/SELL LIMIT
            order = client.create_order(
                symbol=TRADE_SYMBOL,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=QUANTITY,
                price=limit,
                timeInForce=TIME_IN_FORCE_GTC)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    print("sending order")
    print(order)
    order_id = order['orderId']
    return True

def is_order_filled(order_id_x):
    global last_order,order_id,side_buy
    if DEBUG : return True
    if not order_id_x == 0:
        if FUTURE:
            if FUTURE_COIN:
                sorder = client.futures_coin_get_order(symbol=TRADE_SYMBOL,orderId=order_id_x)
            else:
                sorder = client.futures_get_order(symbol=TRADE_SYMBOL,orderId=order_id_x)
        else:
            sorder = client.get_order(symbol=TRADE_SYMBOL,orderId=order_id_x)
        # check if order is filled
        if (sorder['status'] == 'FILLED'):
            if last_order != 0:
                #asyncio.run(save_trade(sorder['side'],sorder['price'],QUANTITY))
                if TWEET : 
                    if GRAPH :
                        asyncio.run(generate_graph()) # problem
                        asyncio.run(post_graph(STRATEGY_NAME+"\n"+str(sorder['side']+":"+str(sorder['price']))))
                    else:
                        asyncio.run(post_twet(STRATEGY_NAME+"\n"+str(sorder['side']+":"+str(sorder['price']))))
                order_id = 0
            last_order = 0
            return True
        elif (sorder['status'] == 'CANCELED'):
            if not side_buy:
                side_buy = True
            last_order = 0
            return True
    return False

# run save older data 
asyncio.run(save_data(client,TRADE_SYMBOL,FUTURE))

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global in_position,order_id,api,test_price,side_buy,last_order,s_order_price,client
    # retrieve last trade
    json_message = json.loads(message)  
    candle = json_message['k']
        
    # run save older data 
    asyncio.run(save_data(client,TRADE_SYMBOL,FUTURE))

    # asyncio.run(save_close(json_message['E'],candle))
    data = pd.read_csv(PATH_DATA).set_index('Date')
    data.index = pd.to_datetime(data.index)

    # retrieve last close price
    close = float(data['Close'][-1])

    print("strategy : " + str(STRATEGY_NAME))
    print("current price :" + str(data['Close'][-1]))
    
    if (order_id==0)|(is_order_filled(order_id)):
        if side_buy:
            r_price = close-(MARGIN*0.2) # to lower buy limit
            side = SIDE_BUY
        else:
            r_price = close+MARGIN 
            side = SIDE_SELL
            
        if (signal(data,close,client)) | (not side_buy) :
            #print(order_id,test_price,r_price)
            if DEBUG:
                if test_price == 0 :
                    asyncio.run(save_trade(side,close,QUANTITY))
                    order_id +=1
                    test_price = close + MARGIN
                else:
                    if close >= test_price:      
                        asyncio.run(save_trade(side,close,QUANTITY))
                        order_id +=1
                        test_price = r_price
            else:  
                print("okay")
                if s_order_price != 0:
                    tickSize_limit = s_order_price
                else:
                    tickf = float(client.get_symbol_info(TRADE_SYMBOL)['filters'][0]["tickSize"])
                    tickSize_limit = round_step_size(
                        r_price,
                        tickf)
                order_limit = order(tickSize_limit,side)
            if side_buy:
                side_buy = False
            else:
                side_buy = True
            last_order = order_id
            s_order_price = 0
        else:
            print("not good")
    else:
        print("wait for order to get filled")
    if DEBUG:
        asyncio.run(generate_graph()) # freezer
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
