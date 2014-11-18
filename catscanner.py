# -*- coding: utf-8 -*-
"""
# cat.py from ib_placeOrder.py in Tradingwithpython
"""

from time import sleep

from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
from ib.ext.Order import Order
#import readBarchart as rdPv
from techStat.SMA import SMA
from techStat.PivotsCSV import PivotsCSV


def mkContract(symbol, secType='STK', exchange='SMART',currency='USD',exp='',strike=0.0,right=''):
	''' create contract object '''
	c = Contract()
	c.m_symbol = symbol
	c.m_secType= secType
	c.m_exchange = exchange
	c.m_currency = currency
	c.m_expiry = exp
	c.m_strike = strike
	c.m_right = right
	return c
	
def mkOrder(id,shares, limit=None, account='U8830832',transmit=0, tif = 'DAY'):
	''' 
	create order object 
	
	Parameters
	-----------
	orderId : The order Id. You must specify a unique value. 
			  When the order status returns, it will be identified by this tag. 
			  This tag is also used when canceling the order.

	shares: number of shares to buy or sell. Negative for sell order.  
	limit : price limit, None for MKT order
	transmit: transmit immideatelly from tws
	'''

	action = {-1:'SELL',1:'BUY'}	
	
	o = Order()
	
	o.m_orderId = id
	o.m_account=account
	o.m_action = action[cmp(shares,0)]
	o.m_totalQuantity = abs(shares)
	o.m_transmit = transmit
	
	if limit is not None:
		o.m_orderType = 'LMT'
		o.m_lmtPrice = limit
	else:
		o.m_orderType = 'MKT'
	
	return o

class MessageHandler(object):
	''' class for handling incoming messages '''
	
	def __init__(self,tws):
		''' create class, provide ibConnection object as parameter '''
		self.nextValidOrderId = None
		
		tws.registerAll(self.debugHandler)
		tws.register(self.nextValidIdHandler,'NextValidId')
		tws.register(self.priceListener,message.tickPrice)
		tws.register(self.priceListener,message.tickSize)
		tws.register(self.orderStatus,message.orderStatus)
		tws.register(self.accountSum,message.accountSummary)
		tws.register(self.updatePos,message.updatePortfolio)
		self.GTAToptSubmitted=False
		
	def nextValidIdHandler(self,msg):
		''' handles NextValidId messages '''
		self.nextValidOrderId = msg.orderId

	def debugHandler(self,msg):
		""" function to print messages """
		#print msg
		
	def priceListener(self,msg):
		#print msg
		qtype = "nada"
		if msg.field == 1:
			qtype = "bid"
			priceDict[msg.tickerId][qtype]=msg.price
		if msg.field == 2:
			qtype = "ask"
			priceDict[msg.tickerId][qtype]=msg.price
		if msg.field == 4:
			qtype = "last"
			priceDict[msg.tickerId][qtype]=msg.price
		if msg.field == 9:
			qtype = "close"
			priceDict[msg.tickerId][qtype]=msg.price
	
		if qtype != "nada" and float(msg.price)>0:
			optstring = ""
				#if float(contractDict[msg.tickerId][5]) > 0.001:
			optlist = []
			optlist.append(str(contractDict[msg.tickerId][4]))
			optlist.append(" ")
			optlist.append(str(contractDict[msg.tickerId][5]))
			optlist.append(" ")
			optlist.append(contractDict[msg.tickerId][6])
			optstring = ''.join([s for s in optlist])
			print '%s: %s: %s: %s: %s' % (contractDict[msg.tickerId][1],
										  contractDict[msg.tickerId][0], optstring, qtype, msg.price)
									  
			if contractDict[msg.tickerId][0]=='GTAT' and float(priceDict[10]['last'])>=19.8 and self.GTAToptSubmitted == False:
				#sell GTAT option
				GTAToptContr=mkContract('GTAT', secType='OPT', exchange='SMART',currency='USD',exp='20150116',strike=20.0,right='CALL')
			
				lmtprice=(float(priceDict[11]['ask'])+float(priceDict[11]['bid']))/2
				if lmtprice<=0: lmtprice=4.0
				GTAToptOrder = mkOrder(self.nextValidOrderId,shares=-10, limit=lmtprice,account='U8852701',transmit=1)
				tws.placeOrder(self.nextValidOrderId, GTAToptContr, GTAToptOrder)
				self.GTAToptSubmitted=True

		#buy tsla option if stock price approaches SMA120
		if contractDict[msg.tickerId][0]=='TSLA':
			if priceDict[2]['last']>0 and priceDict[2]['last']<numSMA[2][0]+0.5:
				print priceDict[2]['last'], "is lower than", numSMA[3][0]+0.5, "buy tsla option!"
		#tempOrdId=nextOrderId.orderId
		#sctyContract = mkContract('SCTY')
		#sctyOrder = mkOrder(nextOrderId.orderId,100, '1.0')#buy scty option if stock price approaches 60, i.e. SMA200								  

	def accountSum(self,msg):
		if msg.tag=='ExcessLiquidity':
			exliq[msg.account]=msg.value
		print exliq

	def orderStatus(self,msg):   #  callback from TWS when an order is executed
			if msg.status == 'Filled' and int(msg.remaining) == 0 \
			and nextOrderId.orderId == int(msg.orderId) and  \
			int(msg.filled) == shares:
				print '%s %s at %s' % (trade.action,shares,msg.avgFillPrice)
		
	def updatePos(self,msg): # does TWS have the same position that orderStatus made?
		print str(msg.contract.m_symbol),int(msg.position)

#-----------Main script-----------------

contractDict = {}
# Note: Option quotes will give an error if they aren't shown in TWS
contractDict[0] = ('SPX', 'IND', 'CBOE', 'USD', '', 0.0, '')
contractDict[1] = ('COMP', 'IND', 'NASDAQ', 'USD', '', 0.0, '')
contractDict[2] = ('TSLA', 'STK', 'SMART', 'USD', '', 0.0, '')
contractDict[3] = ('SCTY', 'STK', 'SMART', 'USD', '', 0.0, '')
contractDict[4] = ('FEYE', 'STK', 'SMART', 'USD', '', 0.0, '')
contractDict[5] = ('DXCM', 'STK', 'SMART', 'USD', '', 0.0, '')
contractDict[6] = ('AAPL', 'STK', 'SMART', 'USD', '', 0.0, '')
contractDict[7] = ('MDSO', 'STK', 'SMART', 'USD', '', 0.0, '')
contractDict[8] = ('QIHU', 'STK', 'SMART', 'USD', '', 0.0, '')
contractDict[9] = ('JD', 'STK', 'SMART', 'USD', '', 0.0, '')
contractDict[10] = ('GTAT', 'STK', 'SMART', 'USD', '', 0.0, '')
contractDict[11] = ('GTAT', 'OPT', 'SMART', 'USD', '20150116', 20.0, 'CALL')

exliq={'U8830832':0,'U8852701':0,'U8865538':0}
priceDict={}
numSMA={}
pv={}

for i in range(0,len(contractDict)):
	#refer to contradict to find what i corresponds to
	priceDict[i]={'bid':0,'ask':0,'last':0,'close':0}
	numSMA[i]=[SMA(200,contractDict[i][0],contractDict[i][1]),SMA(100,contractDict[i][0],contractDict[i][1]),
				SMA(50,contractDict[i][0],contractDict[i][1]),SMA(20,contractDict[i][0],contractDict[i][1])]
	pv[i]=PivotsCSV(contractDict[i][0],contractDict[i][1])

	print numSMA[i],pv[i]


tws = ibConnection(clientId=1050) # create connection object
handler = MessageHandler(tws) # message handling class

tws.connect() # connect to API

contr={}

for tickId in range(0,len(contractDict)):
	contr[tickId]=mkContract(contractDict[tickId][0], contractDict[tickId][1],
							contractDict[tickId][2],contractDict[tickId][3],
							contractDict[tickId][4],contractDict[tickId][5],
							contractDict[tickId][6])
	tws.reqMktData(tickId, contr[tickId], '', False)



sleep(1) # wait for nextOrderId to come in

#=====================sample order-====================
#orderId = handler.nextValidOrderId # numeric order id, must be unique.
#print 'Placing order with id ', orderId
#contract = mkContract('SCTY',secType='OPT', exchange='SMART',currency='USD',exp='20150116',strike=80.0,right='CALL')
#order = mkOrder(orderId,shares=1, limit=0.01) # create order
#tws.placeOrder(orderId, contract, order) # place order
#########################################################

while True:
	sleep(10)

sleep(5)

print 'Cancelling markect data'
#tws.cancelOrder(orderId) # cancel it.
for tickId in range(0,len(contractDict)):
	tws.cancelMktData(tickId)

print 'All done'
			
tws.disconnect()