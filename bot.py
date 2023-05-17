import arbitrage
import api_trading
import json


# check connection
def check_client_connection():
    response = json.loads(api_trading.api_trading_client.check_connection())
    if response['message'] == 'OK':
        print('--- Client Connection Successful ---')
    else:
        print('--- Client Connection Unsuccessful ---')


def bot_trainer():
    while True:
        arbitrage.exchange_scanner()


if __name__ == '__main__':
    check_client_connection()
    bot_trainer()
