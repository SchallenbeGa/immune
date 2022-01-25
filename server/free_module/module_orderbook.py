from binance.client import Client
import server.config as config

client = Client(config.API_KEY, config.API_SECRET, tld='com',testnet=config.DEBUG)
tickers = client.get_orderbook_tickers()
print(tickers)