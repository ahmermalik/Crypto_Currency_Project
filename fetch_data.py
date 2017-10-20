import requests
url = "https://bittrex.com/api/v1.1/public/getmarketsummaries"

# https://bittrex.com/api/v1.1/public/getmarketsummaries

#Function will fetch all market data from api
        #fuction will be a while loop


while True:
    response = requests.request("GET", url).json()['result']
    for item in response:
        print(item['MarketName'])
        # print(item)

    # print(response.json()['result'])

    # marketName =

    # Create a loop over every result in the array and store it in the database.
    #sleep for 15 minutes and repeat

