import requests
from config import IEX_API_TOKEN

def api_url(ticker, kind, token=IEX_API_TOKEN):
    url = "https://cloud.iexapis.com/stable/stock/" + ticker + "/" + kind+ "?token="+ token
    return url

def dateintify(str):
    if str[0] == 0:
        return int(str[1])
    return int(str)
    
