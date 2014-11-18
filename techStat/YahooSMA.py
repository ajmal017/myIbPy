#read data from HistData and compute SMA

import math as mth
import os.path, time
from collections import OrderedDict
import time, sys, os.path
from datetime import datetime, timedelta
import PyAlgoTrade.pyalgotrade.tools.yahoofinance as yh
from pytz import timezone

def YahooSMA(symb,n,sec='stk'):

	ESTnow = datetime.now(timezone('US/Eastern'))
	EST1y=ESTnow-timedelta(days=365)
	newData = yh.download_csv(symb, EST1y,ESTnow, "d")
	Data=newData.split('\n')

	if len(Data)<n: #no enough data
		print Data[-1]
		return 0

	sum=0
	for i in range(1,n+1):
		price=Data[i].split(',')[-1]
		sum+=float(price)
	return round(sum/n,2)


if __name__ == "__main__":

	if len(sys.argv[1:])>0:
		print sys.argv[1:][1], 'days moving average of', sys.argv[1:][0], 'is:'
		print yahooSMA(sys.argv[1:][0],int(sys.argv[1:][1]))
	else:
		print yahooSMA("^GSPC",200)