import time, sys, os.path
from datetime import datetime, timedelta
import PyAlgoTrade.pyalgotrade.tools.yahoofinance as yh
from pytz import timezone


def yahoo200D(symb):
	fileName = 'HistData/YH'+symb+'200_day.csv'

	ESTnow = datetime.now(timezone('US/Eastern'))
	EST1y=ESTnow-timedelta(days=365)
	newData = yh.download_csv(symb, EST1y,ESTnow, "d")
	file = open(fileName, 'w')
	file.write(newData)
	file.close()

if __name__ == "__main__":
	yahoo200D('TSLA')