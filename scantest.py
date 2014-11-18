import tradingWithPython.lib.interactivebrokers as ib
import urllib2, json, csv, re
from ib.opt import ibConnection, message
from datetime import datetime, timedelta
from pytz import timezone
import pytz

symb='TSLA'
cid='12607212'
url='http://www.google.com/finance/option_chain?cid='+cid+'&output=json'
f=open('HistData/tsla2014.json', 'r')
#response = urllib2.urlopen(url)
js =f.read()
js = re.sub(r"(\w+):", r'"\1":', js)

print "====================================================================="
yopts = json.loads(js)
for call in yopts["calls"]:
	#print call
	if call["vol"]!="-":
		print "large volume call ", call["s"]
		##############err container
		optdt='20'+call["s"][-15:-9]
		if datetime(int(optdt[0:4]), int(optdt[4:6]), int(optdt[6:8]), 2, 0, 0).weekday()==6:
			optdt='20'+call["s"][-15:-11]+'%02d'%(int(call["s"][-11:-9])-1) #example SCTY140920C00095000
		print symb, '---->', optdt, optdt=='20140905', call["strike"],'<----'
		c=ib.mkContract(symb, 'OPT', 'SMART', 'USD', '20140905', float(call["strike"]),'CALL')

		dl = ib.Downloader(debug=True)
		df = dl.getIntradayData(c, (2014,8,29)) 
		############### err container						  
		print df
		#df.to_csv('HistData/'+call["s"]+str(dtdigit[2])+'_'+str(dtdigit[0])+'_'+str(dtdigit[1])+'.csv')
		print df[df['volume']*df['WAP']*100>1000000]
		dl.disconnect()
				#request intraday from ib, be sure to check theocc too
