import requests


r = requests.get('https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=both')



print(r) ##if the API request is successful
print(r.json())         ##will print the json string


