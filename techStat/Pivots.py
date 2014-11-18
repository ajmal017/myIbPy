# -*- coding: utf-8 -*-

import Quandl, pandas
from datetime import datetime, timedelta
from pytz import timezone
import tradingWithPython.lib.yahooFinance as yf

def Pivots(symb,symbec='STK',eday=None):
	if eday== None:
		eday = datetime.now(timezone('US/Eastern'))
	bday=eday-timedelta(days=10)
	symbDict={'INDU':'^DJI','COMP':'^IXIC','SPX':'^GSPC','RUT':'^RUT'}
	if symb in symbDict.keys():
		symb=symbDict[symb]

	if symb=='^DJI':
		Data = Quandl.get("YAHOO/INDEX_DJI", authtoken='977FGLXLZ1wsdKt8DgUH',
							trim_start="%d-%02d-%02d" %(bday.year,bday.month,bday.day), 
							trim_end="%d-%02d-%02d" %(eday.year,eday.month,eday.day))[0:1]
		H=Data['High'].values[-1]
		L=Data['Low'].values[-1]
		C=Data['Close'].values[-1]

	else:
		Data = yf.getHistoricData(symb,bday.timetuple()[0:3],eday.timetuple()[0:3])[['high','low','close','adj_close']] # get data from yahoo finance
		H=Data['high'].values[-1]
		L=Data['low'].values[-1]
		C=Data['close'].values[-1]

	P = (H + L + C) / 3
	#P = (H + L + C + C) / 4
	#P = (H + L + O + O) / 4
	R1 = 2*P-L
	S1 = 2*P-H
	R2 = P+(H-L)
	S2 = P-(H-L)
	R3 = R1+(H-L)
	S3 = S1-(H-L)
	return [round(R3,1),round(R2,1),round(R1,1),round(P,1),round(S1,1),round(S2,1),round(S3,1)]

if __name__ == "__main__":
	print Pivots("RWLK")