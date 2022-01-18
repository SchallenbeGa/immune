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

# get average price for x last trade
sma_d = 2
sma_l = 3
# define the difference between buy/sell price
added_val = 0.001
# contain id of sell limit order
order_id = 0
in_position = False

# init client for binance api
client = Client(config.API_KEY, config.API_SECRET, tld='com',testnet=config.DEBUG)

if TEST :
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


    # # fill buys/sells array with empty data until first trade
    # for x in range(len(data)-len(trade)):
    #     buys.append(np.nan)
    #     sells.append(np.nan)

    # # fill buys/sells with trade price
    # for x in range(len(trade)):
    #     if(trade['Type'][x]=="buy"):
    #         buys.append(trade['Price'][x]-0.2)
    #         sells.append(np.nan)
    #     else:
    #         one_sell = True
    #         sells.append(trade['Price'][x]+0.3)
    #         buys.append(np.nan)

    # check if there is at least 1 trade
    if len(trade)>0 :

        y = 0
        for x in range(len(data)):
            #print(x,y)
            #print(len(trade))
            if y<=len(trade):
                #print(str(data.index.array[x].minute))
                #print(str(trade.index.array[y].minute))
                if (data.index.array[x].minute >= trade.index.array[y].minute) & (data.index.array[x].hour == trade.index.array[y].hour) :
                    #print("fuck")
                    print(str(data.index.array[x]))
                    print(str(trade.index.array[y]))
                    if(trade['Type'][y]=="buy"):
                        print("oky")
                        buys.append(trade['Price'][y]-added_val)
                        sells.append(np.nan)
                    else:
                        one_sell=True
                        sells.append(trade['Price'][y]+added_val)
                        buys.append(np.nan)
                    y+=1
                else:
                    buys.append(np.nan)
                    sells.append(np.nan)
        print("okay")
        print(len(data))
        print(len(buys))
        print(len(sells))
        if one_sell :
            apd = [
                mpf.make_addplot(buys, scatter=True, markersize=200, marker=r'^', color='green'),
                mpf.make_addplot(sells, scatter=True, markersize=200, marker=r'v', color='red')
            ]
        else:
            apd = [mpf.make_addplot(buys, scatter=True, markersize=200, marker=r'^', color='green')]

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
    #id = api.update_status_with_media(tweet_content,"tweettest.png").id
    #if fav:
    #    api.create_favorite(id)

    print("save graph")

# save trade form the bot in trade.csv
async def save_trade(b_s,price):
    async with aiofiles.open('trade.csv', mode='r') as f:
        contents = await f.read()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        contents = contents+str(str(current_time)+","+str(b_s)+","+str(price)+","+str(TRADE_QUANTITY)+"\n")
    async with aiofiles.open('trade.csv', mode='w') as f:
        await f.write(contents)

# save older candle in tst.csv
async def save_data():
    if config.FUTURE:
        klines = client.futures_historical_klines(config.PAIR.upper(), Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")
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
def order(limit,side, quantity=TRADE_QUANTITY, symbol=TRADE_SYMBOL,order_type=ORDER_TYPE_MARKET):
    global order_id
    try:
        # check if order has a price limit
        if limit > 0:
            # place limit order
            if config.FUTURE:
                order = client.futures_create_order(symbol=symbol,side=side,type=FUTURE_ORDER_TYPE_LIMIT,quantity=TRADE_QUANTITY,price=limit,timeInForce=TIME_IN_FORCE_GTC)
            else:
                order = client.create_order(symbol=symbol,side=side,type=ORDER_TYPE_LIMIT,quantity=TRADE_QUANTITY,price=limit,timeInForce=TIME_IN_FORCE_GTC)
        else:
            # place market order
            if config.FUTURE:
                client.futures_change_leverage(symbol=symbol, leverage=config.FUTURE_LEVERAGE)
                order = client.futures_create_order(symbol=symbol,side=side,type=order_type, quantity=quantity)
            else:
                order = client.create_order(symbol=symbol,side=side,type=order_type, quantity=quantity)

        print("sending order")
        print(order)
        order_id = order['orderId']
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return True

# run save older data 
asyncio.run(save_data())

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global in_position,order_id,api,added_val,sma_d,sma_l

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

    # retrieve last close price
    close = float(candle['c'])

    asyncio.run(twet_graph("test",True))
    #df = pd.DataFrame(client.futures_order_book(symbol=TRADE_SYMBOL))
    #print(df[['bids', 'asks']].head())
    print("current price :",close)
    print("lower than : ",sma_long," higher than : ",sma)
    # sell section
    if in_position:
        # retrieve sell limit order from binance
        sorder = client.get_order(symbol=TRADE_SYMBOL,orderId=order_id)
        # check if order is filled
        if sorder['status'] == 'FILLED':
            in_position = False

            # save graph (post on twitter)
            # asyncio.run(twet_graph(str(sorder['price']),True))

            # save sell trade in trade.csv
            asyncio.run(save_trade("sell",sorder['price']))
        else:  
            print("waiting for sell : ",sorder)
    else:
    # buy section
        if (close > sma):
            order_succeeded = order(0,SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            if order_succeeded:
                in_position = True

                # save buy trade in trade.csv
                asyncio.run(save_trade("buy",close))

                # defines the intervals that a price/stopPrice can be increased/decreased by
                # https://binance-docs.github.io/apidocs/delivery/en/#filters
                tickf = float(client.get_symbol_info(config.PAIR.upper())['filters'][0]["tickSize"])

                tickSize_limit = round_step_size(
                    close + added_val,
                    tickf)

                # create sell limit order
                order_sell_limit = order(tickSize_limit,SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)

                # check if order had been placed
                if order_sell_limit:
                    # save graph (post on twitter)
                    # asyncio.run(twet_graph("buy",False))
                    print("success sell limit")
                else:
                    print("fail sell limit")
            else:
                print("fail buy")
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
