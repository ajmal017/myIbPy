# from ib_api_demo.py

from time import sleep
import math as mth
import IbHistDataCSV as hD
import readBarchart as rdPv

def saveQuote(msg):
	qtype = "nada"
	if msg.field == 1:
		qtype = "bid"
		priceDic[qtype][contractDict[msg.tickerId][0]]=msg.price
	if msg.field == 2:
		qtype = "ask"
		priceDic[qtype][contractDict[msg.tickerId][0]]=msg.price
	if msg.field == 4:
		qtype = "last"
		priceDic[qtype][contractDict[msg.tickerId][0]]=msg.price
	if msg.field == 9:
		qtype = "close"
		priceDic[qtype][contractDict[msg.tickerId][0]]=msg.price
	
	if qtype != "nada":
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

def portfolioHandler(msg):
	print msg
	print msg.contract.m_symbol

def orderStatus(msg):   #  callback from TWS when an order is executed
	if trade.status == 'executing':
		if msg.status == 'Filled' and int(msg.remaining) == 0 \
		and nextOrderId.orderId == int(msg.orderId) and  \
		int(msg.filled) == shares:
			print '%s %s at %s' % (trade.action,shares,msg.avgFillPrice)
			if trade.action == 'buy':
				trade.pos += shares; trade.action = 'none'
			elif trade.action == 'sell':
				trade.pos -= shares; trade.action = 'none'
			updatePos.status = 'wantUpdate'

def updateEnd(msg): # portfolio update ended (with no position data found)
	if updatePos.status == 'updating':
		print '* * * * POSITION SET TO ZERO * * * *'
		trade.pos = 0
		updatePos.secs = updatePos.countdown
		updatePos.status = 'matched'
		if trade.status == 'waiting': trade.status = 'ready'

def updatePos(msg): # does TWS have the same position that orderStatus made?
	if updatePos.status == 'updating':
		#print str(msg.contract.m_symbol),int(msg.position)
		if str(msg.contract.m_symbol) == contractTuple[0]:
			if trade.pos == int(msg.position):
				updatePos.secs = updatePos.countdown
				updatePos.status = 'matched'
				if trade.status == 'waiting': trade.status = 'ready'
			else:
				print '* * * * POSITION CHANGED * * * *'
				trade.pos = int(msg.position)
				updatePos.status = 'wantUpdate'

def nextOrderId(msg):
	nextOrderId.orderId = msg.orderId-1


def mkStkContract(symbol, secType='STK', exchange='SMART',currency='USD'):
	''' contract factory function '''
	contract = Contract()
	contract.m_symbol = symbol
	contract.m_secType = secType
	contract.m_exchange = exchange
	contract.m_currency = currency
	
	return contract

def touchS1(symb,price):
	if price<S1[symb]: return True
	return False


def touched(key,price):
    if price<S1[symb]: return True
    return False

def crossup(key,price):
    if price<S1[symb]: return True
    return False

def crossdown(key,price):
    if price<S1[symb]: return True
    return False
