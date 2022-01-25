import matplotlib,mplfinance as mpf,pandas as pd,numpy as np
matplotlib.use("Agg")
import free_module.bot_tweet


async def twet_graph(tweet_content,fav):

    global api,sma_d

    buys = []
    sells = []

    one_sell = False

    print("start graph")

    # retrieve chart data
    data = pd.read_csv(f'../data/data.csv').set_index('Date')
    data.index = pd.to_datetime(data.index,format="%Y-%m-%d %H:%M:%S")

    # retrieve trade
    trade = pd.read_csv(f'../data/trade.csv').set_index('Date')
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
                            buys.append(trade['Price'][y])
                            inCandleTrade = True
                        else:
                            print("buy in same candle "+str(y))
                        n = True
                    else:
                        one_sell=True
                        sells.append(trade['Price'][y])
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
            figscale=1,
            figratio=(20,10),
            datetime_format="%d %H:%M:%S",
            xrotation=0,
            returnfig=True)
       
    # save graph in png  
    fig.savefig('tweettest.png',facecolor='#282828')
    if fav:
        bot_tweet.post_graph(tweet_content)
