import aiofiles
from binance.client import Client
from datetime import datetime

PATH_TRADE = f'data/trade.csv'
PATH_DATA = f'data/data.csv'
PATH_ORDER = f'data/order.csv'

# save trade form the bot in trade.csv
async def save_trade(b_s,price,quantity):
    async with aiofiles.open(PATH_TRADE, mode='r') as f:
        contents = await f.read()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        contents = contents+str(str(current_time)+","+str(b_s)+","+str(price)+","+str(quantity)+"\n")
    async with aiofiles.open(PATH_TRADE, mode='w') as f:
        await f.write(contents)

# save order form the bot in order.csv
async def save_order(b_s,price,quantity,status,order_id):
    async with aiofiles.open(PATH_ORDER, mode='r') as f:
        contents = await f.read()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        contents = contents+str(str(current_time)+","+str(status)+","+str(b_s)+","+str(price)+","+str(quantity)+","+str(order_id)+"\n")
    async with aiofiles.open(PATH_ORDER, mode='w') as f:
        await f.write(contents)

# save older candle in tst.csv
# todo : 2h & 1min
async def save_data(client,pair,future):
    if future: 
        klines = client.futures_historical_klines(pair, Client.KLINE_INTERVAL_1MINUTE, "2 hour ago UTC")
    else:
        klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")
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
