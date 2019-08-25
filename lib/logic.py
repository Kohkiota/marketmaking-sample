#!/usr/bin/python
import time
import python_bitbankcc
from functools import lru_cache
from pubnub.pubnub import PubNub
from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration

API_KEY = '6aa60c72-ae58-436a-81c1-b0726efed734'
API_SECRET = '6658fa295ac10defdcc8b607fe76ed4a5724127687408105d3d6801212e0f8d2'
api = python_bitbankcc.private(API_KEY, API_SECRET)
orderAmount = 0.01
maxHoldBtc = 1.0
spreadPercentage = 0.001
pair = 'btc_jpy'

def trade(ask, bid):
    print('--- prepare to trade ---')
    assets = api.get_asset()

    btc = [x for x in assets['assets'] if x['asset'] == 'btc']
    btcAvailable = float(btc[0]['free_amount'])
    jpy = [x for x in assets['assets'] if x['asset'] == 'jpy']
    jpyAvailable = float(jpy[0]['free_amount'])

    # active orders
    activeOrders = api.get_active_orders(pair)
    ids = [str(order['order_id']) for order in activeOrders['orders']]
    # cancel orders
    if len(ids) > 0:
        print('--- cancel all active orders ---')
        print('\n'.join(map(str, ids)))
        cancel_orders = api.cancel_orders(pair, ids)

    # new orders
    bestBid = bid
    bestAsk = ask
    spread = (bestBid + bestAsk) * 0.5 * spreadPercentage
    buyPrice = bestBid - spread
    sellPrice = bestAsk + spread

    if (btcAvailable > maxHoldBtc):
        return False

    # buy order
    if jpyAvailable > buyPrice * orderAmount:
        print("--- buy order ---\n{0}: {1}".format(buyPrice, orderAmount))
        ask = api.order(pair, buyPrice, orderAmount, "buy", "limit")
        # print(ask)
    # sell order
    if btcAvailable > orderAmount:
        print("--- sell order ---\n{0}: {1}".format(sellPrice, orderAmount))
        bid = api.order(pair, sellPrice, orderAmount, "sell", "limit")
        # print(bid)

    return True

