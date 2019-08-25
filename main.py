#!/usr/bin/python
import time
import python_bitbankcc
from pubnub.pubnub import PubNub
from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from lib import logic

SUBSCRIBE_KEY = 'sub-c-e12e9174-dd60-11e6-806b-02ee2ddab7fe'
TICKER_CHANNEL = 'ticker_btc_jpy'
pair = 'btc_jpy'

class BitbankSubscriberCallback(SubscribeCallback):
    def __init__(self, ask, bid):
        self.ask = ask
        self.bid = bid

    def presence(self, pubnub, presence):
        pass # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            # This event happens when radio / connectivity is lost
            pubnub.reconnect()
        elif status.category == PNStatusCategory.PNTimeoutCategory:
            # do some magic and call reconnect when ready
            pubnub.reconnect()
        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            print("Successfully connected.")
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
            print("Successfully re-connected.")

    def message(self, pubnub, message):
        # handle new message stored in message.message
        ret = message.message['data']
        self.ask = float(ret['sell'])
        self.bid = float(ret['buy'])
        print("best ask:{0}, best bid: {1}".format(ret['sell'], ret['buy']))

def main():
    pb = python_bitbankcc.public()
    btc = pb.get_ticker(pair)

    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = SUBSCRIBE_KEY
    pubnub = PubNub(pnconfig)

    # inherits SubscribeCallBack class
    my_listener = BitbankSubscriberCallback(float(btc['sell']), float(btc['buy']))
    pubnub.add_listener(my_listener)
    pubnub.subscribe().channels(TICKER_CHANNEL).execute()

    while True:
        print("Calling the trade logic, best_ask {0}: best_bid {1}".format(my_listener.ask, my_listener.bid))
        logic.trade(my_listener.ask, my_listener.bid)
        time.sleep(10)

if __name__ == '__main__':
    main()

