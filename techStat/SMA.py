#read data from Quandl and compute SMA

import math as mth
import Quandl, pandas
from datetime import datetime, timedelta
from pytz import timezone
import tradingWithPython.lib.yahooFinance as yf

def SMA(symb,intvs,symbec='STK',eday=None):
	if eday==None:
		eday = datetime.now(timezone('US/Eastern'))
	bday=eday-timedelta(days=365)
	symbDict={'INDU':'^DJI','COMP':'^IXIC','SPX':'^GSPC','RUT':'^RUT'}
	if symb in symbDict.keys():
		symb=symbDict[symb]
	if symb=='^DJI':
		Data = Quandl.get("YAHOO/INDEX_DJI", authtoken='977FGLXLZ1wsdKt8DgUH',
							trim_start="%d-%02d-%02d" %(bday.year,bday.month,bday.day), 
							trim_end="%d-%02d-%02d" %(eday.year,eday.month,eday.day))

		sums=list()
		for n in intvs:
			if len(Data.index)<n: #no enough data
				sums.append(-1)
			else:
				sums.append(round(Data['Adjusted Close'][-n-1:-1].mean(),1))

	else:
		Data = yf.getHistoricData(symb,bday.timetuple()[0:3],eday.timetuple()[0:3])[['adj_close']] # get data from yahoo finance
		print Data.tail()
		sums=list()
		for n in intvs:
			if len(Data.index)<n: #no enough data
				sums.append(-1)
			else:
				sums.append(round(Data['adj_close'][-n-1:-1].mean(),1))

	return sums


if __name__ == "__main__":
	print SMA("SCTY",[200,100,50,20],'STK')