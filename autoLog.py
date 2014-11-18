#!/usr/bin/env python
import time, sys, urllib2, re, json
from generateHTML import generateHTML
from getPrevDayStat import getPrevDayStat
from techStat.SMA import SMA
from techStat.Pivots import Pivots
import gdata.sites.client
import gdata.sites.data
from preMktScan import preMktScan


if __name__ == "__main__":
	# Connect to google site

	secdict = json.load(open("localsec.json"))

	SOURCE_APP_NAME = 'dongningInvest-invelon-v1'

	client = gdata.sites.client.SitesClient(source=SOURCE_APP_NAME, site='investelon', domain=None)
	client.ClientLogin(secdict["gaccount"], secdict["gpass"], client.source)

	uri = '%s?kind=%s' % (client.make_content_feed_uri(),'webpage')
	feed = client.GetContentFeed(uri=uri)
	old_entry = feed.entry[0]

	contractDict = {}
	# Note: Option quotes will give an error if they aren't shown in TWS
	contractDict[0] = ('SPX', 'IND', 'CBOE', 'USD', '', 0.0, '')
	contractDict[1] = ('COMP', 'IND', 'NASDAQ', 'USD', '', 0.0, '')
	contractDict[2] = ('INDU', 'IND', 'NYSE', 'USD', '', 0.0, '')
	contractDict[3] = ('RUT', 'IND', 'SMART', 'USD', '', 0.0, '')
	contractDict[4] = ('TSLA', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[5] = ('SCTY', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[6] = ('FB', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[7] = ('AAPL', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[8] = ('DXCM', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[9] = ('MDSO', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[10] = ('BBRY', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[11] = ('FEYE', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[12] = ('AMZN', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[13] = ('TWTR', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[14] = ('DDD', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[15] = ('ILMN', 'STK', 'SMART', 'USD', '', 0.0, '')
	contractDict[16] = ('UBNT', 'STK', 'SMART', 'USD', '', 0.0, '')
	#contractDict[4] = ('1211', 'STK', 'SEHK', 'HKD', '', 0.0, '') #need local symbol his.m_symbol = "HHI.HK"; this.m_localSymbol = "61649"

	numSMA={} 
	for i in range(0,len(contractDict)):
		numSMA[i]=SMA(symb=contractDict[i][0],intvs=[200,100,50,20],symbec=contractDict[i][1])

	#pvDict = {0:'R3',1:'R2',2:'R1',3:'Pivot',4:'S1',5:'S2',6:'S3'}
	pv={}
	for i in range(0,len(contractDict)):
		pv[i]=Pivots(contractDict[i][0],contractDict[i][1])
	
	ldt=urllib2.urlopen('http://download.finance.yahoo.com/d/quotes.csv?s=^IXIC&f=d1').readline()
	dtdigit={}
	digit=0
	for match in re.finditer(r'\d+',ldt):
		dtdigit[digit]=int(ldt[match.start():match.end()])
		digit+=1

	title="%d/%02d/%02d" %(dtdigit[2],dtdigit[0],dtdigit[1])

	premkt=preMktScan()
	html=generateHTML(contractDict,numSMA,pv,premkt)
	try:
		client.CreatePage('announcementspage', title, html)
		print 'New page created!'
	except:
		print "Already updated today!"
		#sys.exit()			#comment out this if need update the summary page

	old_entry.content.html=html
	updated_entry = client.Update(old_entry)
	print 'Home page updated!'