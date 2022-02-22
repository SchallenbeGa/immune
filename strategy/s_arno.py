def s_arno(data,close,risk,period):
  if data['Close'][-3]>data['Close'][-2]>data['Close'][-1]:
    if (data['Close'][-3]-data['Close'][-2]) > (data['Close'][-2]-data['Close'][-1]):
      maybe reverse
      if close > data['Close'][-1]):
        confirm reverse
        if close < data['High'].idxmax:
          diff = close-higher_price
          if diff > (close*0.1):
            #difference between higher and actual price is higher than 10%
            
 
    
    return False

def search_for_lower_price(data):
  min = data['Low'].idxmin
  return order(min)
  
def higher_price(data):
  max = data['High'].idxmax
  return order(max)
