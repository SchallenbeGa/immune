import matplotlib
matplotlib.use("Agg")
import websocket, json, config, tweepy, aiofiles,pandas as pd,asyncio,numpy as np,mplfinance as mpf
from binance.client import Client
from binance.enums import *
from binance.helpers import round_step_size
from datetime import datetime

# retrieve twitter keys
consumer_key = config.C_KEY
consumer_secret = config.C_SECRET
access_token = config.A_T
access_token_secret = config.A_T_S

# set twitter api keys
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

TRADE_SYMBOL = config.PAIR.upper()
TRADE_QUANTITY = config.QUANTITY
TEST = config.DEBUG

side_buy = True

# get average price for x last trade
sma_d = 2
sma_l = 3
# define the difference between buy/sell price
margin = 0.0008
# contain id of sell limit order
order_id = 0
in_position = False

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

# clear tst.csv/trade.csv
with open("tst.csv", "w") as f: 
    f.write("Date,Open,High,Low,Close,Volume")

with open("trade.csv", "w") as f: 
    f.write("Date,Type,Price,Quantity\n")

# create/save graph with buy/sell indicators (& post on twitter) format PNG
async def twet_graph(tweet_content,fav):

    global api,sma_d

    buys = []
    sells = []

    one_sell = False

    print("start graph")

    # retrieve chart data
    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index,format="%Y-%m-%d %H:%M:%S")

    # retrieve trade
    trade = pd.read_csv('trade.csv').set_index('Date')
    trade.index = pd.to_datetime(trade.index,format="%Y-%m-%d %H:%M:%S")

    # create custom style for graph
    s  = mpf.make_mpf_style(
        base_mpf_style="yahoo",
        facecolor="#282828",
        gridcolor="#212121",
        rc={'xtick.color':'#f8f8f8','ytick.color':'#f8f8f8','axes.labelcolor':'#f8f8f8'})

    # check if there is at least 1 trade
    if len(trade)>0 :
        for x in range(len(data)):
            n = False
            inCandleTrade = False
            for y in range(len(trade)):
                if (data.index.array[x].minute == trade.index.array[y].minute) & (data.index.array[x].hour == trade.index.array[y].hour) :
                    if(trade['Type'][y]=="BUY"):
                        print("okay")
                        if not inCandleTrade:
                            buys.append(trade['Price'][y]-margin)
                            inCandleTrade = True
                        else:
                            print("buy in same candle "+str(y))
                        n = True
                    else:
                        one_sell=True
                        sells.append(trade['Price'][y]+margin)
                        n = True
                if len(buys)>len(sells):
                    sells.append(np.nan)
                elif len(buys)<len(sells):
                    buys.append(np.nan)
            if not n:
                buys.append(np.nan)
                sells.append(np.nan)
        print(len(data),len(buys),len(sells))
        if one_sell :
            apd = [
                mpf.make_addplot(buys, scatter=True, markersize=120, marker=r'^', color='green'),
                mpf.make_addplot(sells, scatter=True, markersize=120, marker=r'v', color='red')
            ]
        else:
            apd = [mpf.make_addplot(buys, scatter=True, markersize=120, marker=r'^', color='green')]
        fig,ax = mpf.plot(
            data,
            addplot=apd,
            type='candle',
            volume=True,
            style=s,
            mav=(sma_d,sma_l),
            figscale=1,
            figratio=(20,10),
            datetime_format="%d %H:%M:%S",
            xrotation=0,
            returnfig=True)
    else:  

        fig,ax = mpf.plot(
            data,
            type='candle',
            volume=True,
            style=s,
            mav=(sma_d,sma_l),
            figscale=1,
            figratio=(20,10),
            datetime_format="%d %H:%M:%S",
            xrotation=0,
            returnfig=True)
       
    # save graph in png  
    fig.savefig('tweettest.png',facecolor='#282828')    
    # post graph on twitter and get id
    if fav:
        id = api.update_status_with_media(tweet_content,"tweettest.png").id
        api.create_favorite(id)

    print("save graph")

# save trade form the bot in trade.csv
async def save_trade(b_s,price):
    async with aiofiles.open('trade.csv', mode='r') as f:
        contents = await f.read()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        contents = contents+str(str(current_time)+","+str(b_s)+","+str(price)+","+str(TRADE_QUANTITY)+"\n")
    async with aiofiles.open('trade.csv', mode='w') as f:
        await f.write(contents)

# save older candle in tst.csv
async def save_data():
    if config.FUTURE: 
        klines = client.futures_historical_klines(config.PAIR.upper(), Client.KLINE_INTERVAL_1MINUTE, "2 hour ago UTC")
    else:
        klines = client.get_historical_klines(config.PAIR.upper(), Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")
    async with aiofiles.open('tst.csv', mode='w') as f:
        await f.write("Date,Open,High,Low,Close,Volume")
        for line in klines:
            await f.write(f'\n{datetime.fromtimestamp(line[0]/1000)}, {line[1]}, {line[2]}, {line[3]}, {line[4]},{line[5]}')

# save last candle/close in tst.csv
async def save_close(data):
    async with aiofiles.open('tst.csv', mode='r') as f:
        contents = await f.read()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        contents = contents+"\n"+str(current_time)+","+str(data['o'])+","+str(data['h'])+","+str(data['l'])+","+str(data['c'])+","+str(data['v'])
    async with aiofiles.open('tst.csv', mode='w') as f:
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

# strategy rsi
def s_rsi(data):
    sma = data['Close'][-sma_d:].mean()
    sma_long = data['Close'][-sma_l:].mean()

    if sma < sma_long :
        return True
    else:
        return False

def s_sma(data,close):
    global sma_d,sma_l
    sma = data['Close'][-sma_d:].mean()
    sma_long = data['Close'][-sma_l:].mean()

    if (close > sma) & (close < sma_long):
        return True
    else:
        return False

def signal(data,close):

    switch={
      1:s_sma(data,close),
      2:s_rsi(data)
      }
    if switch.get(config.RISK,"Invalid input"):
        print("good signal")
        return True
    else:
        print("bad signal")
    return False

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
                asyncio.run(twet_graph(str(sorder['side']+":"+str(sorder['price'])),True))
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
    global in_position,order_id,api,margin,sma_d,sma_l,test_price,side_buy,last_order
    # retrieve last trade
    json_message = json.loads(message)  
    candle = json_message['k']

    # is_candle_closed = candle['x']
    # if is_candle_closed:
    #     asyncio.run(twet_graph(":)",False))
        
    # run save older data 
    asyncio.run(save_data())

    # asyncio.run(save_close(json_message['E'],candle))
    data = pd.read_csv('tst.csv').set_index('Date')
    data.index = pd.to_datetime(data.index)

    # calculate moving average
    sma = data['Close'][-sma_d:].mean()
    sma_long = data['Close'][-sma_l:].mean()
    sma_xtralong = data['Close'][-sma_l+sma_d:].mean()

    # retrieve last close price
    # print(candle)
    close = float(candle['c'])

    #df = pd.DataFrame(client.futures_order_book(symbol=TRADE_SYMBOL))
    #print(df[['bids', 'asks']].head())
    print("current price :" + str(close))
    print("lower than : ",sma_long," higher than : ",sma)
    
    if (order_id==0)|(is_order_filled(order_id)):
        if side_buy:
            r_price = close - margin # to lower buy limit
            side = SIDE_BUY
        else:
            r_price = close+margin 
            side = SIDE_SELL
            
        if (signal(data,close)) | (not side_buy) :
            print(order_id,test_price,r_price)
            if TEST:
                if test_price == 0 :
                    asyncio.run(save_trade(side,close))
                    order_id +=1
                    test_price = close + margin
                else:
                    if close >= test_price:      
                        asyncio.run(save_trade(side,close))
                        order_id +=1
                        test_price = r_price
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
        else:
            print("not good")
    else:
        print("wait for order to get filled")
    if TEST:
        asyncio.run(twet_graph("test",False)) # freezer
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
