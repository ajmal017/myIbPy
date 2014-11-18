from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import ibConnection, message
import time, sys, os.path
from datetime import datetime, timedelta
from generateHTML import generateHTML
import IbHistDataCSV as hD
import PyAlgoTrade.pyalgotrade.tools.yahoofinance as yh
from getPrevDayStat import getPrevDayStat
from techStat.SMA import SMA
from techStat.PivotsCSV import PivotsCSV
import readBarchart as rdPv
import gdata.sites.client
import gdata.sites.data
from pytz import timezone


def cleanMerge(seq1,seq2):
	seen = set(seq1)  #merge seq2 into seq1 without repeating.
	if seq1[0].split(',')[3:6]==[0,0,0]:
		seen={x[0:10] for x in seen}
		seq1.extend([ x for x in seq2 if x[0:9] not in seen])
	else:
		seq1.extend([ x for x in seq2 if x not in seen])
	return seq1

if __name__ == "__main__":
	# Connect to google site
	SOURCE_APP_NAME = 'dongningInvest-invelon-v1'

	client = gdata.sites.client.SitesClient(source=SOURCE_APP_NAME, site='investelon', domain=None)
	client.ClientLogin('dongning.wang@gmail.com', 'Ljgoogle2254', client.source)

	uri = '%s?kind=%s' % (client.make_content_feed_uri(),'webpage')
	feed = client.GetContentFeed(uri=uri)
	old_entry = feed.entry[0]

	contractDict = {}
	# Note: Option quotes will give an error if they aren't shown in TWS
	contractDict[0] = ('^GSPC', 'IND', 'CBOE', 'USD', '', 0.0, '')
	contractDict[1] = ('^IXIC', 'IND', 'NASDAQ', 'USD', '', 0.0, '')
	contractDict[2] = ('^DJI', 'IND', 'NYSE', 'USD', '', 0.0, '')
	contractDict[3] = ('^RUT', 'IND', 'NYSE', 'USD', '', 0.0, '')

	contractDict[4] = ('TSLA', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[5] = ('SCTY', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[6] = ('FEYE', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[7] = ('DXCM', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[8] = ('AAPL', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[9] = ('MDSO', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[10] = ('QIHU', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[11] = ('JD', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[4] = ('1211', 'STK', 'SEHK', 'HKD', '', 0.0, '') #need local symbol his.m_symbol = "HHI.HK"; this.m_localSymbol = "61649"
	ESTnow = datetime.now(timezone('US/Eastern'))

	for i in range(0,len(contractDict)):
		fileName = hD.genFileName(contractDict[i][0],contractDict[i][1],'1_day_yh')
		yh.download_daily_bars(contractDict[i][0], 2013, fileName)

	for i in range(0,len(contractDict)):
		fileName = hD.genFileName(contractDict[i][0],contractDict[i][1],'1_day_yh')
		print fileName
		
		if os.path.isfile(fileName): # found a previous version
			file = open(fileName, 'r')
			oldRowData = file.readlines()
			file.close()
			prevRec=len(oldRowData)
			# get the new end date and time from the last data line of the file
			lastRow = oldRowData[-1]
			lastRowData=lastRow.split(",")
			print lastRowData[0]
			lastDay=datetime.strptime(lastRowData[0], "%Y-%m-%d")
			duration=(ESTnow.replace(tzinfo=None)-lastDay).days
			print duration
			newData = yh.download_csv(contractDict[i][0], datetime(int(lastDay.year), int(lastDay.month), int(lastDay.day)),
									datetime(int(ESTnow.year), int(ESTnow.month), int(ESTnow.day)), "d")
			allData=cleanMerge(oldRowData,newData)
			file = open(fileName, 'w')
			file.write(allData)
			file.close()
		else:
			oldRowData = [] # no old file
			prevRec=0
			oldRowData.append('Year,Month,Day,Hour,Minute,Second,Open,High,Low,Close,Volume\n')
			allData=cleanMerge(oldRowData,newData)
			file = open(fileName, 'w')
			file.write(allData)
			file.close()
			
		print len(allData)-prevRec,' of CSV data appended to file: ', fileName
		
#	numSMA={} 
#	for i in range(0,len(contractDict)):
#		numSMA[i]=[SMA(200,contractDict[i][0],contractDict[i][1]),SMA(100,contractDict[i][0],contractDict[i][1]),SMA(50,contractDict[i][0],contractDict[i][1]),SMA(20,contractDict[i][0],contractDict[i][1])]
#		print numSMA[i]
	
	#pvtsla=rdPv.readPv('TSLA')
	#sleep(5)
	#pvscty=rdPv.readPv('SCTY')
	
	#pvDict = {0:'R3',1:'R2',2:'R1',3:'Pivot',4:'S1',5:'S2',6:'S3'}
#	pv={}
#	for i in range(0,len(contractDict)):
#		pv[i]=PivotsCSV(contractDict[i][0],contractDict[i][1])

#	fileName = hD.genFileName(contractDict[0][0],contractDict[0][1],'1_day')
#	try: 	
#		file = open(fileName, 'r')
#		Data = file.readlines()
#		file.close()
#	except:
#		print "no such file!"
#		sys.exit()

#	lastRow = Data[-1]
#	lData=lastRow.split(",")		
#	title=lData[2]+'/'+lData[1]+'/'+lData[0]
#	try:
#		client.CreatePage('announcementspage', title, generateHTML(contractDict,numSMA,pv))
#		print 'New page created!'
#	except:
#		print "Already updated today!"
#		sys.exit()			#comment out this if need update the summary page

#	print "--------updating CSV..."
#	for i in range(0,len(contractDict)):
#		hD.IbHistDataCSV(contractDict[i][0],sec=contractDict[i][1], exch=contractDict[i][2])
#		numSMA[i]=[SMA(200,contractDict[i][0],contractDict[i][1]),SMA(100,contractDict[i][0],contractDict[i][1]),SMA(50,contractDict[i][0],contractDict[i][1]),SMA(20,contractDict[i][0],contractDict[i][1])]
#		print numSMA[i]
#	print "--------CSV historic data updated--------"

#	for i in range(0,len(contractDict)):
#		pv[i]=PivotsCSV(contractDict[i][0],contractDict[i][1])

#	old_entry.content.html=generateHTML(contractDict,numSMA,pv)

#	updated_entry = client.Update(old_entry)
#	print 'Home page updated!'