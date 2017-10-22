import requests
import time
from models import Currency
url = "https://bittrex.com/api/v1.1/public/getmarketsummaries"

# https://bittrex.com/api/v1.1/public/getmarketsummaries

#Function will fetch all market data from api
        #fuction will be a while loop


while True:
    response = requests.request("GET", url).json()['result']
    for item in response:

        coin_pair = item['MarketName']
        day_high = item['High']
        day_low = item['Low']
        volume = item['Volume']
        last_price = item['Last']
        base_volume = item['BaseVolume']
        bid_price = item['Bid']
        ask_price = item['Ask']
        open_buy = item['OpenBuyOrders']
        open_sell = item['OpenSellOrders']
        prev_day = item['PrevDay']

        currency = Currency.select().where(Currency.coin_pair == coin_pair)

        if not currency:
            print(coin_pair + ' has been created')
            Currency.create(coin_pair=coin_pair,
                            day_high=day_high,
                            day_low=day_low,
                            volume=volume,
                            last_price=last_price,
                            base_volume=base_volume,
                            bid_price=bid_price,
                            ask_price=ask_price,
                            open_buy=open_buy,
                            open_sell=open_sell,
                            prev_day=prev_day).save()
        elif currency:
            print(coin_pair + ' has been updated')
            Currency.update(day_high=day_high,
                            day_low=day_low,
                            volume=volume,
                            last_price=last_price,
                            base_volume=base_volume,
                            bid_price=bid_price,
                            ask_price=ask_price,
                            open_buy=open_buy,
                            open_sell=open_sell,
                            prev_day=prev_day).where(Currency.coin_pair == coin_pair).execute()

    time.sleep(30)




    # print(response.json()['result'])

    # marketName =

    # Create a loop over every result in the array and store it in the database.
    #sleep for 15 minutes and repeat

