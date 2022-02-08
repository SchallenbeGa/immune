# strategy copy order book
import pandas as pd

def s_order_book(risk,client,pair):
    global s_order_price
    #wip : select minimum volume or minimum margin from last price

    df = pd.DataFrame(client.futures_order_book(symbol=pair))

    if risk == 1:
        order_no = 3
    elif risk == 2:
        order_no = 2
    else :
        order_no = 1

    # get biggest ask order
    #print(df[['asks','bids']].max())
    # get biggest bids order
    #idx = np.argpartition(-df['bids'][...,-1].flatten(), 3)

    s_order_price = df['bids'][order_no][0]   
    if s_order_price != 0:
        print(s_order_price)
        return True
    return False