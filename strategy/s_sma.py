
# strategy sma
def s_sma(data,close,risk,period):

    if risk == 1:
        sma = data['Close'][-(period*3):].mean()
        sma_long = data['Close'][-(period*4):].mean()
        sma_long_x = data['Close'][-100:].mean()
    elif risk == 2:
        sma = data['Close'][-(period*2):].mean()
        sma_long = data['Close'][-(period*3):].mean()
        sma_long_x = data['Close'][-80:].mean()
    else :
        sma = data['Close'][-period:].mean()
        sma_long = data['Close'][-(period+1):].mean()
        sma_long_x = data['Close'][-(period+3):].mean()

    print("-----------------")
    print("sma_short:"+str(sma))
    print("sma_long:"+str(sma_long))
    print("sma_long_x:"+str(sma_long_x))
    if (close > sma) & (close < sma_long) & (close < sma_long_x):
        return True
    
    return False
