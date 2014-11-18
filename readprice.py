import re
import ib
from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
from time import sleep

class Downloader(object):
    field4price = ''
    
    def __init__(self):
        self.tws = ibConnection('localhost', 4001, 0)
        self.tws.register(self.tickPriceHandler, 'TickPrice')
        self.tws.connect()
        self._reqId = 1 # current request id
    
    def tickPriceHandler(self,msg):
        if msg.field == 4:
            self.field4price = msg.price
    print '[debug]', msg
    
    def requestData(self,contract):
        self.tws.reqMktData(self._reqId,c,'',1)
        self._reqId+=1

if __name__=='__main__':
    dl = Downloader()
    c = Contract()
    c.m_symbol = 'SPY'
    c.m_secType = 'STK'
    c.m_exchange = 'SMART'
    c.m_currency = 'USD'
    dl.requestData(c)
    sleep(3)
    print 'Price - field 4: ', dl.field4price