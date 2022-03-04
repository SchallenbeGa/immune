# AUTOMATE BINANCE BUY/SELL

* warning : use at ur own fckn risk
* take care of fees : https://www.binance.com/en/fee/schedule (login to see your fee level)

## CONFIG.PY

   ### BINANCE
    API_KEY = 'ndSdbjSmijYKsKabl4eue3nBcMuxl1eqcHeuawHro9SgRgXVctvJ0YvoozJl3'
    API_SECRET = 'c5dnUZ3sD4G1OzMFzcLUtik7aoUleFzPbikmFmje8nPsUeadeeObTielDeyU'
   ### TWEETER
    TWEET=True
    C_KEY = 'B16J2YTwEBIsXBBWZO42pC'
    C_SECRET = 'R8J9tUI4V0O4BmggOHQuwvHOgRUF1aYFvTlIc010SnD9fuR'
    A_T = '126528524811520-VtPzQN6E3NQsLtnJx91P1GwfYmXPwp'
    A_T_S = 'rWQfTH3dopJ0NhBkH053AtX9HvWrOZaXIUorVVwd'
   ### TELEGRAM
   * To get Telegram module, please follow this tutorial : https://www.siteguarding.com/en/how-to-get-telegram-bot-api-token
   * When you got your TOKEN, open terminal and run : 
    telegram-send --configure
   * Go to server/config.py and turn TELEGRAM=False to True
   * Enjoy :)
   
   ### VAR
    PAIR = 'bnbusdt'
    PAIR_S = 'usdt'
    PAIR_B = "bnb"
    QUANTITY = '20'
   ### ENVIRONMENT
    DEBUG = True
    TESTNET = False
   ### FUTURE
    FUTURE = True
    FUTURE_LEVERAGE = '1'
    FUTURE_COIN = False (wip)
   ### STRATEGY VAR
    STRATEGY_NAME = "sma&rsi" # sma|rsi|orderbook
    RISK = 1 safest (1-3)
    PERIOD = 2 nb trade to anaylse
   ### POSITION
    MARGIN=0.0008

## COMMAND

    python3 bot.py


## IMPORT

      pip install python-binance websocket-client aiofiles pandas asyncio aiocsv numpy matplotlib mplfinance tweepy
      
## TWEETER API | Tweepy API V1.1

### Register
* https://developer.twitter.com/
* https://developer.twitter.com/en/apps
click on app and replace "setting" by "auth-settings" in url,

        https://developer.twitter.com/en/portal/projects/xxxx/apps/xxxx/" <- !auth-settings
           
### Activate oauth 1.0a put on

        Callback URI / Redirect URL -> http://twitter.com
        Website URL -> http://twitter.com
        
        
        consumer_key = 'nGZ2GOUnmJheVWj5ZagsG'
        consumer_secret = 'Yc7iFcuDFlNxQbEapIuSsN7OUOaWaH931VwRdOGjFjgy'
        access_token = '1265285941624811-yCEprankedSFWmHLCFcqHfHSQPKplJZ'
        access_token_secret = 'NkvqRUgBuhX9QWP2j2EHO3S640KOIxDgCaVuGC'


## LIBRARIES

 * https://python-binance.readthedocs.io/en/latest/index.html
 * https://pypi.org/project/websocket-client/
 * https://pypi.org/project/aiofiles/
 * https://pypi.org/project/asyncio/
 * https://github.com/matplotlib/mplfinance
 * https://docs.tweepy.org/en/stable/
## TODO
   
   * COINPICKER WITH PARAMETER
   * STOP LOSS = FEES + MARGIN/2
