
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

    c_delta = data['Close'][-(period*4):].diff()

    up = c_delta.clip(lower=0)
    down = -1 * c_delta.clip(upper=0)

    ma_up = up.ewm(com = period - 1, adjust=True, min_periods = period).mean()
    ma_down = down.ewm(com = period - 1, adjust=True, min_periods = period).mean()
    
    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))

    print("-----------------")
    print("current rsi:" + str(rsi[-1]))
    print("minimum rsi:" + str(rsi_low))
    print("#################")
    if rsi[-1] < rsi_low :
        return True
    
    return False