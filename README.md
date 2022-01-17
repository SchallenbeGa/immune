# AUTOMATE BINANCE BUY/SELL

CONFIG.PY

    API_KEY = 'lo82VNWUhkdbYUlANMK5TejscD97tXNaDoTx5WT1Qw6kKPj5k4o1EUglbhvyx06r' (BINANCE)
    API_SECRET = 'secret' (BINANCE)
    PAIR = 'xrpusdt'
    PAIR_M = 'XRPUSDT'
    PAIR_S = 'usdt'
    QUANTITY = '50'
    DEBUG = True

COMMAND

    python3 bot.py
    python3 app.py (web server)


IMPORT

      pip install python-binance websocket-client aiofiles pandas asyncio aiocsv numpy mplfinance tweepy
      
# TWEETER API | Tweepy API V1.1

## Register
* https://developer.twitter.com/
* https://developer.twitter.com/en/apps
click on app and replace "setting" by "auth-settings" in url,

        https://developer.twitter.com/en/portal/projects/xxxx/apps/xxxx/" <- !auth-settings
           
## Activate oauth 1.0a put on

        Callback URI / Redirect URL -> http://twitter.com
        Website URL -> http://twitter.com
        
        
        consumer_key = 'nGZ2GOUnmJheVWj5ZagsKG'
        consumer_secret = 'Yc7iFcuDFlNxQbEapIuSsN7OUO9aWaH931VwRdOGjFjgy'
        access_token = '1265285941624811-yCEprankedSFWmHLCFcqHfHSQPKplJZ'
        access_token_secret = 'NkvqRUgBuhX9WQWP2j2EHO3S640KOIxDgCaVuGC'


# LIBRARIES

 * https://python-binance.readthedocs.io/en/latest/index.html
 * https://pypi.org/project/websocket-client/
 * https://pypi.org/project/aiofiles/
 * https://pypi.org/project/asyncio/
 * https://github.com/matplotlib/mplfinance
 * https://docs.tweepy.org/en/stable/

# PROBLEM

## in test
 * If insufficient balance -> python3 WARNING_TEST_ONLY.py (it will sell all config.pair_B for config.pair_S)
