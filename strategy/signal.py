# choose/combine strategy
from server.config import PERIOD,RISK,PAIR,STRATEGY_NAME
from strategy.s_rsi import *
from strategy.s_order_book import *
from strategy.s_sma import *

multi = True # combine strategy


def signal(data,close,client,side_buy):
    # multi strategy signal
    if not side_buy : return True
    if STRATEGY_NAME == "sma":
        return s_sma(data,close,RISK,PERIOD)
    elif STRATEGY_NAME == "rsi":
        return s_rsi(data,RISK,PERIOD)
    else:
        return s_order_book(RISK,client,PAIR.upper())
