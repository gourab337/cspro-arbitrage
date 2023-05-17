from cryptography.hazmat.primitives.asymmetric import ed25519
from urllib.parse import urlparse, urlencode
import urllib
import json
import requests
from decouple import config

class ApiTradingClient:

  secret_key = None,
  api_key = None

  def __init__(self, secret_key:str, api_key:str):
        self.secret_key = secret_key
        self.api_key = api_key
        self.base_url = "https://coinswitch.co"
        self.headers = {
            "Content-Type": "application/json"
        }


  def call_api(self, url: str, method: str, headers: dict = None, payload:dict = {}):
    '''
    make an API call on webserver and return response

    Args:
      url (str): The API url to be called
      method (str): The API method
      headers (dict): required headers for API call
      payload (dict): payload for API call

    Returns:
      json: The response of the request
    '''
    final_headers = self.headers.copy()
    if headers is not None:
      final_headers.update(headers)
    
    response = requests.request(method, url, headers=headers, json=payload)
    return response.json()


  def signatureMessage(self, method: str , url: str, payload: dict):
    '''
      Generate signature message to be signed for given request

      Args:
        url (str): The API url to be called
        method (str): The API method
        payload (dict): payload for API call

      Returns:
        json: The signature message for corresponding API call
    '''
    message = method + url + json.dumps(payload, separators=(',', ':'), sort_keys=True)
    return message


  def get_signature_of_request(self, secret_key: str, request_string: str) -> str:
    '''
      Returns the signature of the request
      
      Args:
        secret_key (str): The secret key used to sign the request.
        request_string (str): The string representation of the request.

      Returns:
        str: The signature of the request.
    '''
    request_string = bytes(request_string, 'utf-8')
    secret_key_bytes = bytes.fromhex(secret_key)
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
    signature_bytes = secret_key.sign(request_string)
    signature = signature_bytes.hex()
    return signature


  def make_request(self, method:str, endpoint:str, payload:dict = {}, params:dict = {}):
    '''
    Make the request to :
      a. generate signature message
      b. generate signature signed by secret key
      c. send an API call with the encoded URL

    Args:
        method (str): The method to call API
        endpoint (str): The request endpoint to make API call
        payload (dict): The payload to make API call for POST request
        params (dict): The params to make GET request

      Returns:
        dict: The response of the request.

    '''
    decoded_endpoint = endpoint
    if method == "GET" and len(params)!=0:
      endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
      decoded_endpoint = urllib.parse.unquote_plus(endpoint)

    signature_msg = self.signatureMessage(method, decoded_endpoint, payload)

    signature = self.get_signature_of_request(self.secret_key, signature_msg)

    headers = {
        "X-AUTH-SIGNATURE" : signature,
        "X-AUTH-APIKEY": self.api_key
    }

    url = f"{self.base_url}{endpoint}"

    response = self.call_api(url, method, headers = headers, payload = payload)
    return json.dumps(response, indent=4)


  def check_connection(self):
    return self.make_request("GET", "/api-trading-service/api/v1/ping")

  def create_order(self,payload:dict = {}):
    return self.make_request("POST", "/api-trading-service/api/v1/order/create", payload = payload)

  def cancel_order(self, payload:dict = {}):
    return self.make_request("PUT", "/api-trading-service/api/v1/order/cancel", payload = payload)

  def get_open_orders(self, params:dict = {}):
    return self.make_request("GET", "/api-trading-service/api/v1/orders/get/open", params = params)

  def get_closed_orders(self, params:dict = {}):
    return self.make_request("GET", "/api-trading-service/api/v1/orders/get/closed", params = params)

  def get_user_portfolio(self):
    return self.make_request("GET", "/api-trading-service/api/v1/user/portfolio")

  def get_24h_all_pairs_data(self, params:dict = {}):
    return self.make_request("GET", "/api-trading-service/api/v1/ticker/24hr/all-pairs", params = params)

  def get_24h_coin_pair_data(self, params:dict = {}):
    return self.make_request("GET", "/api-trading-service/api/v1/ticker/24hr", params = params)

  def get_depth(self, params:dict = {}):
    return self.make_request("GET", "/api-trading-service/api/v1/depth", params = params)

  def get_trades(self, params:dict = {}):
    return self.make_request("GET", "/api-trading-service/api/v1/trades", params = params)

  def get_candelstick_data(self, params:dict = {}):
    return self.make_request("GET", "/api-trading-service/api/v1/getDataForCandlestick", params = params)
  
  def get_exchange_precision(self, payload:dict = {}):
    return self.make_request("POST", "/api-trading-service/api/v1/exchange-precision", payload = payload)


secret_key = config('SECRET_KEY')
api_key = config('CS_PRO_API_KEY')
api_trading_client = ApiTradingClient(secret_key, api_key)

#check connection
# print(api_trading_client.check_connection())

#create order
# payload = {
#   "deposit_amount": 160,
#   "deposit_currency": "inr",
#   "destination_currency": "btc",
#   "expiry_period": 90,
#   "limit_price": 2200000,
#   "type": "LIMIT",
#   "exchange_name": "WAZIRX",
#   "uuid": "ee15d0e9-de1e-46af-a6e4-451234"
# }
# print(api_trading_client.create_order(payload=payload))

#cancel order
# payload = {
#     "order_id": "98cbfc4d-aacd-4848-9521-714237d434b4",
#     "action": "DELETE"
# }
# print(api_trading_client.cancel_order(payload=payload))

#get portfolio
# print(api_trading_client.get_user_portfolio())

#get open orders
# params = {
#   "page": 1,
#   "count": 1,
#   "from_date": "2022-12-1",
#   "to_date": "2023-5-8",
#   "trade_type": "buy",
#   "currency": '''["btc,inr"]''',
#   "exchange": '''["wx"]''',
#   "order_type": "LIMIT"
# }
# print(api_trading_client.get_open_orders(params = params))

#get closed orders
# params = {
#   "page": 1,
#   "count": 1,
#   "from_date": "2022-12-1",
#   "to_date": "2023-4-8",
#   "trade_type": "sell",
#   "currency": '''["btc,inr"]''',
#   "exchange": '''["csx","wx"]''',
#   "order_type": "LIMIT"
# }
# print(api_trading_client.get_closed_orders(params = params))

# #get ticker 24hr all pair data csx, wx
# params = {
#   "exchange": 'wx'
# }
# print(api_trading_client.get_24h_all_pairs_data(params=params))

#get ticker data of coin pair
# params = {
#   "symbol": "btc,inr",
#   "exchange": '["csx"]'
# }
# print(api_trading_client.get_24h_coin_pair_data(params=params))

# get candelstick data
# params = {
#   "to_time": "1662681600000",
#   "from_time": "1647388800000",
#   "symbol": "BTCINR",
#   "c_duration": 1440,
#   "exchange": "wx"
# }
# print(api_trading_client.get_candelstick_data(params=params))

# #get depth
# params = {
#   "exchange": "csx",
#   "symbol": "btc,inr"
# }
# print(api_trading_client.get_depth(params = params))

# get trades
# params = {
#   "exchange": "csx",
#   "symbol": "btc,inr"
# }
# print(api_trading_client.get_trades(params=params))

# get exchange precision
# payload = {
#     "exchange_name":"csx"
# }
# print(api_trading_client.get_exchange_precision(payload = payload))