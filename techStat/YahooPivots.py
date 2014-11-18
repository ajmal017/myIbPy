# -*- coding: utf-8 -*-
#compute pivots from yahoo finance data

import PyAlgoTrade.pyalgotrade.tools.yahoofinance as yh

def YahooPivots(symb):
    url = "http://ichart.finance.yahoo.com/table.csv?s=%s" %symb
    f = urllib2.urlopen(url)
    if f.headers['Content-Type'] != 'text/csv':
        return [-1,-1,-1,-1,-1,-1,-1]
    newData=f.read()
    Data=newData.split('\n')

    lastRow = Data[1]
    rec=lastRow.split(",")
    print "calculating pivots of ",symb, "from CSV data updated on ", rec[0],"/",rec[1],"/",rec[2]

    P =(float(rec[2])+float(rec[3])+float(rec[-1]))/3
	#P = (H + L + C) / 3
	#P = (H + L + C + C) / 4
	#P = (H + L + O + O) / 4
    R1 = 2*P-float(rec[3])
    S1 = 2*P-float(rec[2])
    M=float(rec[2])-float(rec[3])
    R2 = P+M
    S2 = P-M
    R3 = R1+M
    S3 = S1-M

if __name__ == "__main__":
	print PivotsCSV('^IXIC')