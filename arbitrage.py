import api_trading
import json
from decimal import *
import time
import csv
from datetime import datetime


# function to write to high_earners.csv
def csv_writer(output):
    with open('high_earners.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(output)


# Calculates exchange arbitrage opportunity
def arbitrage_calculator(exchange_coin):
    params = {
        "symbol": f"{exchange_coin}",
        "exchange": '["wx"]'
    }
    wazirx_response = json.loads(api_trading.api_trading_client.get_24h_coin_pair_data(params=params))
    print(wazirx_response)
    wazirx_price = Decimal(wazirx_response["data"]["WX"]["lastPrice"])

    params = {
        "symbol": f"{exchange_coin}",
        "exchange": '["csx"]'
    }
    csx_response = json.loads(api_trading.api_trading_client.get_24h_coin_pair_data(params=params))
    print(csx_response)
    csx_price = Decimal(csx_response["data"]["CSX"]["lastPrice"])

    # delta +ve implies sell in wazirx, delta -ve means sell in csx
    delta = csx_price - wazirx_price
    if delta == 0:
        print("No arbitrage opportunity!")
    else:
        print("Possible arbitrage opportunity!")
        print(f"Coin Name: {exchange_coin}")
        if delta > 0:
            exchange = 'wx'
        else:
            exchange = 'csx'
        print("Sell at: ", exchange)
        params = {
            "symbol": f"{exchange_coin}",
            "exchange": f'["{exchange}"]'
        }
        exchange_response = json.loads(api_trading.api_trading_client.get_24h_coin_pair_data(params=params))
        print(exchange_response)
        required_investment = Decimal(exchange_response["data"][exchange.upper()]["lastPrice"])
        roi = abs(delta / required_investment)
        print(f"ROI: {roi}")
        # Setting edge considering 1% TDS on buy and sell (0.01 + 0.01)
        edge = 0.02
        if roi >= edge:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            output = [current_time, exchange_coin, exchange, roi]
            csv_writer(output)


# Scans through all the exchange coins and runs arbitrage_calculator method on them.
def exchange_scanner():
    # Coins available in both CSX and WazirX
    tradable_coin_list = ["BTC,INR", "ETH,INR", "MATIC,INR", "REQ,INR", "1INCH,INR", "USDT,INR", "LRC,INR", "DOGE,INR", "LTC,INR", "TRX,INR", "XRP,INR", "FTM,INR", "SAND,INR", "BNB,INR", "YFI,INR", "CHR,INR", "UNI,INR", "XLM,INR", "OMG,INR", "BAT,INR", "ZRX,INR"]
    print(len(tradable_coin_list))
    for exchange_coin in tradable_coin_list:
        exchange_coin = exchange_coin.lower()
        arbitrage_calculator(exchange_coin)
        # Delay to handle API ratelimit
        # time.sleep(9)
        print("\n")


if __name__ == '__main__':
    # Init CSV Writer
    header = ['Time', 'Coin Name', 'Sell at', 'ROI']
    csv_writer(header)
    exchange_scanner()



 # ["BTC,INR", "ETH,INR", "MATIC,INR", "REQ,INR", "1INCH,INR", "USDT,INR", "LRC,INR", "DOGE,INR", "LTC,INR", "TRX,INR", "XRP,INR", "FTM,INR", "SAND,INR", "BNB,INR", "YFI,INR", "CHR,INR", "UNI,INR", "XLM,INR", "OMG,INR", "BAT,INR", "ZRX,INR", "SHIB,INR", "UMA,INR", "CRV,INR", "MKR,INR", "SXP,INR", "COMP,INR", "IOST,INR", "COTI,INR", "GALA,INR", "BICO,INR"]