import requests
import time


currency_url = "https://bittrex.com/api/v1.1/public/getmarketsummaries"

market_url = "https://bittrex.com/api/v1.1/public/getmarkets"

bid_spread ="https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=both"

coin_pair="BTC-LTC"
# market_response = requests.request("GET", currency_url).json()['result']

bid_market_response = requests.request("GET", currency_url).json()['result']

print(bid_market_response)