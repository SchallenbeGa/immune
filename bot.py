from ast import Return
import websocket, json, server.config as config, aiofiles,pandas as pd,asyncio,numpy as np
from binance.client import Client
from binance.enums import *
from free_module.bot_graph import *
from binance.helpers import round_step_size
from datetime import datetime

TRADE_SYMBOL = config.PAIR.upper()
TRADE_QUANTITY = config.QUANTITY
TEST = config.DEBUG

PATH_TRADE = f'data/trade.csv'
PATH_DATA = f'data/data.csv'
# get average price for x last trade
PERIOD = config.PERIOD
# define the difference between buy/sell price
MARGIN = config.MARGIN
# contain id of sell limit order
order_id = 0
in_position = False
# start with a buy
side_buy = True 
s_order_price = 0
last_order = 0

test_price = 0
# init client for binance api
client = Client(config.API_KEY, config.API_SECRET, tld='com',testnet=config.TESTNET)

if config.TESTNET :
    # use testnet wss
    SOCKET = "wss://testnet.binance.vision/ws/"+config.PAIR+"@kline_1m"
else:
    SOCKET = "wss://stream.binance.com:9443/ws/"+config.PAIR+"@kline_1m"

if config.FUTURE:
    SOCKET = "wss://fstream.binance.com/ws/"+config.PAIR+"@kline_1m"
    #client.API_URL = 'https://fapi.binance.com'

# clear data.csv/trade.csv
with open(PATH_DATA, "w") as f: 
    f.write("Date,Open,High,Low,Close,Volume")

with open(PATH_TRADE, "w") as f: 
    f.write("Date,Type,Price,Quantity\n")

# save trade form the bot in trade.csv
async def save_trade(b_s,price):
    async with aiofiles.open(PATH_TRADE, mode='r') as f:
        contents = await f.read()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        contents = contents+str(str(current_time)+","+str(b_s)+","+str(price)+","+str(TRADE_QUANTITY)+"\n")
    async with aiofiles.open(PATH_TRADE, mode='w') as f:
        await f.write(contents)

# save older candle in tst.csv
async def save_data():
    if config.FUTURE: 
        klines = client.futures_historical_klines(config.PAIR.upper(), Client.KLINE_INTERVAL_1MINUTE, "2 hour ago UTC")
    else:
        klines = client.get_historical_klines(config.PAIR.upper(), Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")
    async with aiofiles.open(PATH_DATA, mode='w') as f:
        await f.write("Date,Open,High,Low,Close,Volume")
        for line in klines:
            await f.write(f'\n{datetime.fromtimestamp(line[0]/1000)}, {line[1]}, {line[2]}, {line[3]}, {line[4]},{line[5]}')

# save last candle/close in tst.csv
async def save_close(data):
    async with aiofiles.open(PATH_DATA, mode='r') as f:
        contents = await f.read()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        contents = contents+"\n"+str(current_time)+","+str(data['o'])+","+str(data['h'])+","+str(data['l'])+","+str(data['c'])+","+str(data['v'])
    async with aiofiles.open(PATH_DATA, mode='w') as f:
        await f.write(contents)

# place order on binance
def order(limit,side, quantity=TRADE_QUANTITY, symbol=TRADE_SYMBOL):
    global order_id
    #order_id = 0
    try:
        # place limit order
        if config.FUTURE:
            client.futures_change_leverage(symbol=symbol, leverage=config.FUTURE_LEVERAGE)
            if config.FUTURE_COIN: # COIN-M wip
                order = client.futures_coin_create_order(
                    symbol=symbol,
                    side=side,
                    type=FUTURE_ORDER_TYPE_LIMIT,
                    quantity=TRADE_QUANTITY,
                    price=limit,
                    timeInForce=TIME_IN_FORCE_GTC)
            else: # USD-M
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=FUTURE_ORDER_TYPE_LIMIT,
                    quantity=TRADE_QUANTITY,
                    price=limit,
                    timeInForce=TIME_IN_FORCE_GTC)
        else: # SPOT BUY/SELL LIMIT
            order = client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=TRADE_QUANTITY,
                price=limit,
                timeInForce=TIME_IN_FORCE_GTC)
        print("sending order")
        print(order)
        order_id = order['orderId']
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return True

# strategy copy order book
def s_order_book(risk):
    global s_order_price
    #wip : select minimum volume or minimum margin from last price

    df = pd.DataFrame(client.futures_order_book(symbol=TRADE_SYMBOL))

    if risk == 1:
        order_no = 3
    elif risk == 2:
        order_no = 2
    else :
        order_no = 1

    #get biggest ask order
    #print(df[['asks','bids']].max())
    #get biggest bids order
    #idx = np.argpartition(-df['bids'][...,-1].flatten(), 3)

    s_order_price = df['bids'][order_no][0]   
    if s_order_price != 0:
        print(s_order_price)
        return True
    return False

# strategy rsi
def s_rsi(data,risk,period):

    if risk == 1:
        rsi_low = 30
        period*=3
    elif risk == 2:
        rsi_low = 35
        period*=2
    else :
        rsi_low = 40

    c_delta = data['Close'][-period*4:].diff()

    up = c_delta.clip(lower=0)
    down = -1 * c_delta.clip(upper=0)

    ma_up = up.ewm(com = period - 1, adjust=True, min_periods = period).mean()
    ma_down = down.ewm(com = period - 1, adjust=True, min_periods = period).mean()
    
    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))
    
    if rsi[-1] < rsi_low :
        return True
    
    print("current rsi:" + str(rsi[-1]))
    print("minimum rsi:" + str(rsi_low))
    return False

#strategy sma
def s_sma(data,close,risk,period):

    if risk == 1:
        sma = data['Close'][-(period*3):].mean()
        sma_long = data['Close'][-(period*4):].mean()
    elif risk == 2:
        sma = data['Close'][-(period*2):].mean()
        sma_long = data['Close'][-(period*3):].mean()
    else :
        sma = data['Close'][-period:].mean()
        sma_long = data['Close'][-(period+1):].mean()

    if (close > sma) & (close < sma_long):
        return True
    
    print("sma_short:"+str(sma))
    print("sma_long:"+str(sma_long))
    return False

def signal(data,close):
    if config.STRATEGY_NAME == "sma":
        return s_sma(data,close,config.RISK,PERIOD)
    elif config.STRATEGY_NAME == "rsi":
        return s_rsi(data,config.RISK,PERIOD)
    else:
        return s_order_book(config.RISK)

def is_order_filled(order_id):
    global last_order
    if TEST : return True
    if not order_id == 0:
        if config.FUTURE:
            if config.FUTURE_COIN:
                sorder = client.futures_coin_get_order(symbol=TRADE_SYMBOL,orderId=order_id)
            else:
                sorder = client.futures_get_order(symbol=TRADE_SYMBOL,orderId=order_id)
        else:
            sorder = client.get_order(symbol=TRADE_SYMBOL,orderId=order_id)
        # check if order is filled
        if (sorder['status'] == 'FILLED'):
            if last_order != 0:
                asyncio.run(save_trade(sorder['side'],sorder['price']))
                asyncio.run(twet_graph(config.STRATEGY_NAME+"\n"+str(sorder['side']+":"+str(sorder['price'])),True))
            last_order = 0
            return True
    return False

# run save older data 
asyncio.run(save_data())

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global in_position,order_id,api,test_price,side_buy,last_order,s_order_price
    # retrieve last trade
    json_message = json.loads(message)  
    candle = json_message['k']
        
    # run save older data 
    asyncio.run(save_data())

    # asyncio.run(save_close(json_message['E'],candle))
    data = pd.read_csv(PATH_DATA).set_index('Date')
    data.index = pd.to_datetime(data.index)

    # retrieve last close price
    close = float(candle['c'])

    print("strategy : " + str(config.STRATEGY_NAME))
    print("current price :" + str(close))
    
    if (order_id==0)|(is_order_filled(order_id)):
        if side_buy:
            r_price = close - (MARGIN/2) # to lower buy limit
            side = SIDE_BUY
        else:
            r_price = close+MARGIN 
            side = SIDE_SELL
            
        if (signal(data,close)) | (not side_buy) :
            #print(order_id,test_price,r_price)
            if TEST:
                if test_price == 0 :
                    asyncio.run(save_trade(side,close))
                    order_id +=1
                    test_price = close + MARGIN
                else:
                    if close >= test_price:      
                        asyncio.run(save_trade(side,close))
                        order_id +=1
                        test_price = r_price
            else:  
                print("okay")
                if s_order_price != 0:
                    tickSize_limit = s_order_price
                else:
                    tickf = float(client.get_symbol_info(config.PAIR.upper())['filters'][0]["tickSize"])
                    tickSize_limit = round_step_size(
                        r_price,
                        tickf)
                order_limit = order(tickSize_limit,side, TRADE_QUANTITY, TRADE_SYMBOL)
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
    if TEST:
        asyncio.run(twet_graph(config.STRATEGY_NAME+"\n"+"test",False)) # freezer
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
