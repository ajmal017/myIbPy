#!/usr/bin/env python
# -*- coding: utf-8 -*-

# requests the past day data from TWS return open close high low 


from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
import os.path, time
from collections import OrderedDict
from techStat.SMA import SMA


def contract(contractTuple):
	newContract = Contract()
	newContract.m_symbol = contractTuple[0]
	newContract.m_secType = contractTuple[1]
	newContract.m_exchange = contractTuple[2]
	newContract.m_currency = contractTuple[3]
	newContract.m_expiry = contractTuple[4]
	newContract.m_strike = contractTuple[5]
	newContract.m_right = contractTuple[6]
	print 'Contract Parameters: [%s,%s,%s,%s,%s,%s,%s]' % contractTuple
	return newContract


# convert UTC to New York EST timezone
def ESTtime(msg):
	return time.gmtime(int(msg.date) - (5 - time.daylight)*3600)

def strDatetime(dt):
	return dt[0:4]+','+dt[4:6]+','+dt[6:8]+','+dt[10:12]+','+dt[13:15]+','+dt[16:18]

def dataWatcher(msg):
	if int(msg.high) > 0:
		dataWatcher.pricesWatched =[msg.open,msg.high,msg.low,msg.close]
		dataWatcher.finished = True

def watchAll(msg):
	print msg
	
def errHandler(msg):
	if msg.errorMsg.find('data farm connection is OK')==False:
		print msg

def getPrevDayStat(sym, sec='STK', exch='SMART'):
	con = ibConnection(clientId=1050)
	con.registerAll(watchAll)
	con.unregister(watchAll, message.historicalData)
	con.register(dataWatcher, message.historicalData)
	con.unregister(watchAll, message.error)
	con.register(errHandler, message.error)

	con.connect()
	time.sleep(1)
	contractTuple = (sym, sec, exch, 'USD', '', 0.0, '')
	
	endSecs = time.time()-(5-time.daylight)*60*60  # to NY EST via gmtime
	NYtime = time.gmtime(endSecs)
	
	# combined dateStr+timeStr format is 'YYYYMMDD hh:mm:ss TMZ'
	dateStr = time.strftime('%Y%m%d', NYtime)
	timeStr = time.strftime(' %H:%M:%S EST', NYtime)
	dataWatcher.pricesWatched =[0,0,0,0]

	dataWatcher.finished = False # true when historical data is done
	con.reqHistoricalData(0,
					  contract(contractTuple),
					  dateStr+timeStr, # last requested bar date/time
					  '2 D',  # quote duration, units: S,D,W,M,Y
					  '1 day',  # bar length
					  'TRADES',  # what to show
					  0, 1 )
	countSecs = 0
	while not dataWatcher.finished and countSecs < 5: # wait up to 20 seconds
		time.sleep(1)
		countSecs += 1
	if dataWatcher.finished==False:
		con.reqHistoricalData(0,
						  contract(contractTuple),
						  dateStr+timeStr, # last requested bar date/time
						  '1 D',  # quote duration, units: S,D,W,M,Y
						  '1 day',  # bar length
						  'TRADES',  # what to show
						  0, 1 )
		countSecs = 0
		while not dataWatcher.finished and countSecs < 5: # wait up to 20 seconds
			time.sleep(1)
			countSecs += 1	
	con.disconnect()
	print dataWatcher.pricesWatched
	return dataWatcher.pricesWatched

if __name__ == "__main__":
#IbHistDataCSV('COMP',sec='IND', exch='NASDAQ', duration='1 Y')
	contractDict = {}
	# Note: Option quotes will give an error if they aren't shown in TWS
	contractDict[1] = ('COMP', 'IND', 'NASDAQ', 'USD', '', 0.0, '')
	contractDict[2] = ('TSLA', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[3] = ('SCTY', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[4] = ('1211', 'STK', 'SEHK', 'HKD', '', 0.0, '') #need local symbol his.m_symbol = "HHI.HK"; this.m_localSymbol = "61649"
	
	priceDic={'bid':{},'ask':{},'last':{},'close':{}}
	
	for i in range(1,len(contractDict)+1):
		print getPrevDayStat(contractDict[i][0],sec=contractDict[i][1], exch=contractDict[i][2])
