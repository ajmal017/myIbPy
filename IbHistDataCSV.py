#!/usr/bin/env python
# -*- coding: utf-8 -*-

# requests historical data from TWS and can save to a CSV file

# bar length is set to 15 minute bars

# legal bar lengths: 1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min,
#	 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour,
#	 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1 week, 1 month

# the data duration is set to 1 year (28800 seconds)

# can read/write a CSV OHLC file
#   if the file exists, the first file date/time becomes the inital request
#   so earlier historical data is requested and put at the front of the file

# uses Eastern Standard Time for data requests and writing date/time to CSV

# return the date and time of the last record

from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
import os.path, time
from collections import OrderedDict
from techStat.SMA import SMA
from datetime import datetime, timedelta
from pytz import timezone

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

def cleanMerge(seq1,seq2):
	seen = set(seq1)  #merge seq2 into seq1 without repeating.
	if seq1[0].split(',')[3:6]==[0,0,0]:
		seen={x[0:9] for x in seen}
		seq1.extend([ x for x in seq2 if x[0:9] not in seen])
	else:
		seq1.extend([ x for x in seq2 if x not in seen])
	return seq1


# convert UTC to New York EST timezone
def ESTtime(msg):
	return time.gmtime(int(msg.date) - (5 - time.daylight)*3600)

def strDatetime(dt):
	return dt[0:4]+','+dt[4:6]+','+dt[6:8]+','+dt[10:12]+','+dt[13:15]+','+dt[16:18]

def printData(msg):
	if int(msg.high) > 0:
		dataStr =  '%s,%s,%s,%s,%s,%s' % (strDatetime(msg.date),
										  msg.open,
										  msg.high,
										  msg.low,
										  msg.close,
										  msg.volume)
		#TODO:
		#do date check here~~!!!!!
		msgdate=datetime(int(msg.date[0:4]),int(msg.date[4:6]),int(msg.date[6:8]),20,0,0,0,timezone('US/Eastern'))
		if printData.endtime<msgdate:
			if printData.write2file: printData.newRowData.append(dataStr+'\n')
		else: 
			print "old data received, did not add to the record"
	else: printData.finished = True

def watchAll(msg):
	print msg
	
def errHandler(msg):
	try:
		if msg.errorMsg.find('data farm connection is OK')==False:
			print msg
	except:
		print msg

def genFileName(symb,sec,barLength):
	directory="HistData"
	if not os.path.exists(directory):os.makedirs(directory)
	barLengthStr = barLength.replace(" ","_") # add the bar length to the file name
	return directory+'/'+symb+'_'+sec+'_'+barLengthStr+'.csv'	

def IbHistDataCSV(sym, sec='STK', exch='SMART', barLength='1 day', duration='1 Y'):
	con = ibConnection(clientId=1050)
	con.registerAll(watchAll)
	con.unregister(watchAll, message.historicalData)
	con.register(printData, message.historicalData)
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
	
	# write2file=True to write data to: fileName in the default directory
	lastdaycautious=False
	printData.write2file = True
	if printData.write2file:
		fileName = genFileName(contractTuple[0],contractTuple[1],barLength)
		if os.path.isfile(fileName): # found a previous version
			file = open(fileName, 'r')
			oldRowData = file.readlines()
			file.close()
			prevRec=len(oldRowData)
			printData.endtime=datetime(100,1,1,0,0,0,0,timezone('US/Eastern'))
			if prevRec > 1:
				# get the new end date and time from the last data line of the file
				lastRow = oldRowData[-1]
				lastRowData=lastRow.split(",")
				endtimeStr = ' %s:%s:%s EST' % (lastRowData[3],lastRowData[4],lastRowData[5])
				printData.endtime=datetime(int(lastRowData[0]),int(lastRowData[1]),int(lastRowData[2]),20,0,0,0,timezone('US/Eastern'))
				if endtimeStr.find('::') :  #contain "::" means?
					if barLength=='1 day':
						durationnum=(int(dateStr[0:4])-int(lastRow[0:4]))*366+(int(dateStr[4:6])-int(lastRow[5:7]))*31+int(dateStr[6:8])-int(lastRow[8:10])
						ESTnow = datetime.now(timezone('US/Eastern'))
						#print ESTnow
						EST8pm = ESTnow.replace(hour=20, minute=0, second=0, microsecond=0)
						EST4am = ESTnow.replace(hour=4, minute=0, second=0, microsecond=0)
						if ESTnow>EST4am and ESTnow<=EST8pm:
							lastdaycautious=True
							#print lastdaycautious
						if durationnum<1 and ESTnow<EST8pm:
							if ESTnow<EST4am:
								print "You have updated yesterday. The market is not open yet."
							if ESTnow>EST4am and ESTnow<=EST8pm:
								print "wait until the market closes."
							con.disconnect()
							return datetime(100,1,1,0,0,0)
						duration=str(durationnum)+' D'
						print duration
					else:
						print "barlength too short"
						con.disconnect()
						return datetime(100,1,1,0,0,0)
				#barlength is in mins and previous data has time
				elif barLength.find('min')>0:
					duration=str((int(dateStr[6:8])-int(lastRow[8:10]))*24*60+(int(timeStr[1:3])-int(lastRow[11:13]))*60+int(timeStr[4:6])-int(lastRow[14:16]))+' D'
				else:
					print "other unit of time need more work"
					con.disconnect()
					return datetime(100,1,1,0,0,0)
	
		else:
			oldRowData = [] # no old file
			prevRec=0
			oldRowData.append('Year,Month,Day,Hour,Minute,Second,Open,High,Low,Close,Volume\n')
	printData.newRowData = []
	
	printData.finished = False # true when historical data is done
	print 'End Date/Time: [%s]' % (dateStr+timeStr)
	con.reqHistoricalData(0,
					  contract(contractTuple),
					  dateStr+timeStr, # last requested bar date/time
					  duration,  # quote duration, units: S,D,W,M,Y
					  barLength,  # bar length
					  'TRADES',  # what to show
					  0, 1 )
	countSecs = 0
	while not printData.finished and countSecs < 25: # wait up to 20 seconds
		time.sleep(1)
		countSecs += 1
	con.disconnect()
	#print 'CSV format: year,month,day,hour,minute,second,open,high,low,close,volume'
	if printData.write2file:
		Data=cleanMerge(oldRowData,printData.newRowData)
		if lastdaycautious:	#remove the premarket data
			if Data[-1][0:10].replace(',','')==dateStr:
				Data.pop()
				print "pre-market data is removed"
		file = open(fileName, 'w')
		file.writelines(Data)
		file.close()
		print len(Data)-prevRec,' of CSV data appended to file: ', fileName
	
	lastRow = Data[-1]
	lData=lastRow.split(",")

	eastern = timezone('US/Eastern')
	if lData[0]=='Year':
		res=datetime(100,1,1,0,0,0)
	elif lData[3]=='':
		res=eastern.localize(datetime(int(lData[0]), int(lData[1]), int(lData[2]),20,0,0))
	else:
		res=eastern.localize(datetime(int(lData[0]), int(lData[1]), int(lData[2]), int(lData[3]), int(lData[4]), int(lData[5])))
	#print res
	return res

if __name__ == "__main__":
	#example: IbHistDataCSV('COMP',sec='IND', exch='NASDAQ', duration='1 Y')
	contractDict = {}
	# Note: Option quotes will give an error if they aren't shown in TWS
	#contractDict[0] = ('SPX', 'IND', 'CBOE', 'USD', '', 0.0, '')
	#contractDict[1] = ('COMP', 'IND', 'NASDAQ', 'USD', '', 0.0, '')
	contractDict[0] = ('TSLA', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[3] = ('SCTY', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[4] = ('FEYE', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[5] = ('DXCM', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[6] = ('AAPL', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[7] = ('MDSO', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[8] = ('QIHU', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[9] = ('JD', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[0] = ('SCTY', 'OPT', 'SMART', 'USD', '20150116', 80.0, 'CALL')
	#contractDict[4] = ('1211', 'STK', 'SEHK', 'HKD', '', 0.0, '') #need local symbol his.m_symbol = "HHI.HK"; this.m_localSymbol = "61649"
		
	for i in range(0,len(contractDict)):
		IbHistDataCSV(contractDict[i][0],sec=contractDict[i][1], exch=contractDict[i][2], barLength='30 secs', duration='1 D')
