import tradingWithPython.lib.interactivebrokers as ib
import urllib2, json, csv, re, os, pytz
from ib.opt import ibConnection, message
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar


def histOI(symb):
    reader = csv.reader(open('HistData/pooldict.csv', 'rb'))
    sym2cid = dict(x for x in reader)
    #thisy=datetime.now(timezone('US/Eastern')).year
    cid=sym2cid[symb]
    ldt=urllib2.urlopen('http://download.finance.yahoo.com/d/quotes.csv?s=TSLA&f=d1').readline()
    dtdigit={}
    digit=0
    for match in re.finditer(r'\d+',ldt):
        dtdigit[digit]=int(ldt[match.start():match.end()])
        digit+=1
    print dtdigit[2],dtdigit[0],dtdigit[1]
#========================
    rec={}
        #load option chain
    url='http://www.google.com/finance/option_chain?cid='+cid+'&output=json'
    res = urllib2.urlopen(url)
    js =res.read()
    js = re.sub(r"(\w+):", r'"\1":', js)
    optchn = json.loads(js)

    yreqed=set()
    for dt in optchn["expirations"]:
        if dt["y"] not in yreqed:
            yreqed.add(dt["y"])
            #print symb, yreqed
            url='http://www.google.com/finance/option_chain?cid='+cid+'&expy='+str(dt["y"])+'&output=json'
            yres = urllib2.urlopen(url)
            js =yres.read()
            js = re.sub(r"(\w+):", r'"\1":', js)
            yopt = json.loads(js)
            for call in yopt["calls"]:
                #{cid:"435585872657711",name:"",s:"SCTY140912P00062000",e:"OPRA",p:"-",c:"-",b:"0.01",a:"0.05",oi:"0",vol:"-",strike:"62.00",expiry:"Sep 12, 2014"}
                if not call["expiry"] in rec:
                    rec[call["expiry"]]={}

                if call["oi"]=="-": 
                    calloi=0
                else:
                    calloi=int(call["oi"])
                #print rec
                rec[call["expiry"]][call["strike"]]=calloi
    
    fname="HistData/histoi/"+symb+"%04d%02d%02d.json" %(dtdigit[2],dtdigit[0],dtdigit[1])
    fname=str(fname)
    j = json.dumps(rec, indent=4)
    f = open(fname, 'w')
    print >> f, j
    f.close()
    return rec

if __name__ == "__main__":
    fname = 'HistData/pool.csv'

    with open(fname) as f:
        symbols = f.read().splitlines()
        
    for symb in symbols:
        histOI(symb)
