# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

from typing import Dict, List, ClassVar
from datamodel import OrderDepth, TradingState, Order
from math import inf
import pandas as pd

class Trader:
    max_quantities: ClassVar[Dict[str, int]] = {'PEARLS': 20, 'BANANAS': 20, 'COCONUTS': 600, 'PINA_COLADAS': 300}
    min_spreads: ClassVar[Dict[str, int]] = {'PEARLS': 2, 'BANANAS': 3, 'COCONUTS': 3, 'PINA_COLADAS': 3}

    productLimitDict = {"PEARLS":20, "BANANAS":20, 'COCONUTS': 20, 'PINA_COLADAS': 20}
    productAggressionDict = {"PEARLS":0.25, "BANANAS":0.25, 'COCONUTS': 0.25, 'PINA_COLADAS': 0.25}
    stopLossPeriods = 10
    productEmergencyThresholdDict = {"PEARLS": inf,"BANANAS": 0.0001, 'COCONUTS': 0.0001, 'PINA_COLADAS': 0.0001}
    
    def __init__(self):
        self.Tracking = self.createTracking()
    
    def createTracking(self):
        Tracking = {}
        trackingColumns = ["Timestamp","Bid", "Ask", "Mid", "BidVol", "AskVol"]
        for product in self.productLimitDict:
            Tracking[product] = pd.DataFrame(columns = trackingColumns)
        return Tracking


    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        result = {}

        for product in state.listings:
            #Test price of individual asset

            trackingRowDict = self.getTracking(product, state)
            print("\n")
            print(product)
            print(trackingRowDict)

            productPosition = state.position.get(product, 0)
            bidQuantity = self.max_quantities[product] - productPosition
            askQuantity = self.max_quantities[product] + productPosition

            #Detect emergency market
            nPeriodAvgReturn = self.Tracking[product]['Mid'].pct_change().tail(self.stopLossPeriods).mean()
            if nPeriodAvgReturn < -1*self.productEmergencyThresholdDict[product] and productPosition>0:
                print(product,"Emergency Falling Market")
                bidQuantity = 0
            elif nPeriodAvgReturn > self.productEmergencyThresholdDict[product] and productPosition<0:
                print(product,"Emergency Rising Market")
                askQuantity = 0

            bidPrice = trackingRowDict["Bid"][0]
            askPrice = trackingRowDict["Ask"][0]

            if askPrice!=None and bidPrice!=None:
                spread = askPrice - bidPrice
                #modify bid and ask price based on agression dictionary
                bidPrice += self.productAggressionDict[product]*(spread/2)
                askPrice -= self.productAggressionDict[product]*(spread/2)
            else:
                spread = -1 #Invalid Spread

            orders = []

            if spread >= self.min_spreads[product] and bidQuantity > 0:
                orders.append(Order(product, bidPrice, bidQuantity))

            if spread >= self.min_spreads[product] and askQuantity > 0:
                orders.append(Order(product, askPrice, -askQuantity))

            result[product] = orders

        return result

    def getTracking(self, product, state):
        trackingRowDict = {}
        productOrderDepth = state.order_depths[product]
        if len(productOrderDepth.buy_orders)>0:
            bid = max(productOrderDepth.buy_orders.keys())
            bidVol = productOrderDepth.buy_orders[bid]
        else:
            bid = None
            bidVol = None
        
        if len(productOrderDepth.sell_orders)>0:
            ask = min(productOrderDepth.sell_orders.keys())
            askVol = productOrderDepth.sell_orders[ask]
        else:
            ask = None
            askVol = None

        if bid!=None and ask!=None:
            mid = (bid+ask)/2
        else:
            mid = None

        trackingRowDict = {
            "Timestamp":[state.timestamp],
            "Bid":[bid],
            "Ask":[ask],
            "Mid":[mid],
            "BidVol":[bidVol],
            "AskVol":[askVol],
        }
        
        #update tracking DataFrame
        self.Tracking[product] = pd.concat([self.Tracking[product], pd.DataFrame.from_dict(trackingRowDict)])

        return trackingRowDict
