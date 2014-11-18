import tradingWithPython.lib.interactivebrokers as ib
import urllib2, json, csv, re, os, pytz
from ib.opt import ibConnection, message
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar


def preMktScan():
    sym2cid=json.load(open("HistData/pooldict.json"))
    #thisy=datetime.now(timezone('US/Eastern')).year
    ldt=urllib2.urlopen('http://download.finance.yahoo.com/d/quotes.csv?s=TSLA&f=d1').readline()
    dtdigit={}
    digit=0
    for match in re.finditer(r'\d+',ldt):
        dtdigit[digit]=int(ldt[match.start():match.end()])
        digit+=1
    print dtdigit[2],dtdigit[0],dtdigit[1]

#look up short squeeze candidates
    url='http://www.theocc.com/webapps/threshold-securities?reportDate=%d%02d%02d'% (dtdigit[2],dtdigit[0],dtdigit[1])
    cont=urllib2.urlopen(url).read()
    bday_us = CustomBusinessDay(calendar=USFederalHolidayCalendar())
    dt = datetime(int(dtdigit[2]), int(dtdigit[0]), int(dtdigit[1]))-bday_us
    lastdty=dt.year
    lastdtm=dt.month
    lastdtd=dt.day

    if cont.find('File requested')>-1:
        url='http://www.theocc.com/webapps/threshold-securities?reportDate=%d%02d%02d'% (lastdty,lastdtm,lastdtd)
        cont=urllib2.urlopen(url).read()

    rdlist=cont.splitlines()
    stklist=[]
    for line in rdlist[1:-1]:
        tmp= line.split('|')
        if tmp[2]=='S' or tmp[2]=='U':
            stklist.append(tmp[0])

    shtsqz='<p>Possible Short Squeeze: '
    for stk in stklist:
        shtsqz+='''<a href="https://www.tradingview.com/chart/%s/"> %s </a>''' % (stk,stk)

    shtsqz+="</p>"
    rv=list()
    rv.append(shtsqz)

#search for 50, 100, 200 MA +/- 3% band.

    #load past option oi record

#========================
    try:
        dl = ib.Downloader(debug=True)
    except:
        print "Shut down other application which might use TWS api!"
    try:
        for symb, cid in sym2cid.items():
            symb=str(symb)
            cid=str(cid)
            putoifname="HistData/histoi/%sPUT%04d%02d%02d.json" % (symb,lastdty,lastdtm,lastdtd)
            calloifname="HistData/histoi/%sCALL%04d%02d%02d.json" % (symb,lastdty,lastdtm,lastdtd)
            try:
                json_data=open(putoifname)
                oldputOI = json.load(json_data)
                json_data.close()

                json_data=open(calloifname)
                oldcallOI = json.load(json_data)
                json_data.close()
            except:
                oldcallOI={}
                oldputOI={}


            #load option chain
            url='http://www.google.com/finance/option_chain?cid='+sym2cid[symb]+'&output=json'
            res = urllib2.urlopen(url)
            js =res.read()
            js = re.sub(r"(\w+):", r'"\1":', js)
            optchn = json.loads(js)

            callOIRec={}
            putOIRec={}
            yreqed=set()
            for dt in optchn["expirations"]:
                if dt["y"] not in yreqed:
                    yreqed.add(dt["y"])
                    #print symb, yreqed
                    url='http://www.google.com/finance/option_chain?cid='+sym2cid[symb]+'&expy='+str(dt["y"])+'&output=json'
                    yres = urllib2.urlopen(url)
                    js =yres.read()
                    js = re.sub(r"(\w+):", r'"\1":', js)
                    yopt = json.loads(js)
                    stkpr=float(yopt["underlying_price"])
                    htmlstr=""
                    for call in yopt["calls"]:
                        if not call["expiry"] in callOIRec:
                            callOIRec[call["expiry"]]={}

                        if call["oi"]=="-": 
                            calloi=0
                        else:
                            calloi=int(call["oi"])
                        #print rec
                        callOIRec[call["expiry"]][call["strike"]]=calloi
                        if call["expiry"] in oldcallOI and call["strike"] in oldcallOI[call["expiry"]]:
                            pcalloi=oldcallOI[call["expiry"]][call["strike"]]
                        else:
                            pcalloi=-1

                        if call["vol"]!="-" and call["p"]!="-" and float(call["p"])<=20:

                            tot=long(call["vol"])*float(call["p"])*100
                            if tot>1000000 and float(call["strike"])>stkpr/2 and float(call["strike"])<stkpr*1.5:
                                
                                htmlstr+='''<table><tr>
                                <td><font color="00cc00">[%s]</font></td> 
                                <td>$ %s CALL expires on %s,</td> 
                                <td> %s hands traded at %s,</td> 
                                <td>total value of %s.</td>
                                <td>OI: %d -> %d </td></tr></table>''' % (symb,call["strike"],call["expiry"],call["vol"],call["p"],"{:,}".format(tot),pcalloi,calloi)
                                print '''[%s] %s hands of %s CALL with strike price %s, total value of %s''' % (symb,call["vol"],call["s"], call["strike"],"{:,}".format(tot))
                                #request intraday from ib, be sure to check theocc too
                                optdt=str('20'+call["s"][-15:-9])
                                if datetime(int(optdt[0:4]), int(optdt[4:6]), int(optdt[6:8]), 2, 0, 0).weekday()==5:
                                    optdt=str('20'+call["s"][-15:-11]+'%02d'%(int(call["s"][-11:-9])-1)) #example SCTY140920C00095000
                                fname='HistData/'+call["s"]+str(dtdigit[2])+'_'+str(dtdigit[0])+'_'+str(dtdigit[1])+'C'+'.csv'
                                #print symb, 'OPT', 'SMART', 'USD', optdt, call["strike"],'CALL'
                                if os.path.isfile(fname):
                                    df=pd.DataFrame().from_csv(fname)
                                else:
                                    c=ib.mkContract(symb, 'OPT', 'SMART', 'USD', optdt, float(call["strike"]),'CALL')

                                    df = dl.getIntradayData(c, (dtdigit[2],dtdigit[0],dtdigit[1]))                            
                                    df.to_csv(fname)

                                lg=df[df['volume']*df['WAP']*100>200000]
                                if not lg.empty:
                                    htmlstr+=lg.to_html()
                                    print lg
                                
                    for put in yopt["puts"]:
                        if not put["expiry"] in putOIRec:
                            putOIRec[put["expiry"]]={}

                        if put["oi"]=="-": 
                            putoi=0
                        else:
                            putoi=int(put["oi"])
                        #print rec
                        putOIRec[put["expiry"]][put["strike"]]=putoi
                        if put["expiry"] in oldputOI and put["strike"] in oldputOI[put["expiry"]]:
                            pputoi=oldputOI[put["expiry"]][put["strike"]]
                        else:
                            pputoi=-1

                        if put["vol"]!="-" and put["p"]!="-" and float(put["p"])<=20:
                            tot=long(put["vol"])*float(put["p"])*100
                            if tot>1000000 and float(put["strike"])>stkpr/2 and float(put["strike"])<stkpr*1.5:
                                htmlstr+='''<table><tr>
                                <td><font color="ff0000">[%s]</font></td> 
                                <td>$ %s PUT expires on %s,</td> 
                                <td> %s hands traded at %s,</td> 
                                <td>total value of %s</td>
                                <td>OI: %d -> %d </td></tr></table>''' % (symb,put["strike"],put["expiry"],put["vol"],put["p"],"{:,}".format(tot),pputoi,putoi)
                                print '''[%s] %s hands of %s PUT with strike price %s, total value of %s''' % (symb,put["vol"],put["s"], put["strike"],"{:,}".format(tot))
                                #request intraday from ib
                                optdt=str('20'+put["s"][-15:-9])
                                if datetime(int(optdt[0:4]), int(optdt[4:6]), int(optdt[6:8]), 2, 0, 0).weekday()==5:
                                    optdt=str('20'+put["s"][-15:-11]+'%02d'%(int(put["s"][-11:-9])-1)) #example SCTY140920C00095000
                                fname='HistData/'+put["s"]+str(dtdigit[2])+'_'+str(dtdigit[0])+'_'+str(dtdigit[1])+'P'+'.csv'
                                #print symb, 'OPT', 'SMART', 'USD', optdt, put["strike"],'PUT'
                                if os.path.isfile(fname):
                                    df=pd.DataFrame().from_csv(fname)
                                else:
                                    c=ib.mkContract(symb, 'OPT', 'SMART', 'USD', optdt, float(put["strike"]),'PUT')

                                    df = dl.getIntradayData(c, (dtdigit[2],dtdigit[0],dtdigit[1]))                            
                                    df.to_csv(fname)

                                lg=df[df['volume']*df['WAP']*100>200000]
                                if not lg.empty:
                                    htmlstr+=lg.to_html()
                                    print lg
                    rv.append(htmlstr)
            #make option open interest record
            fname="HistData/histoi/"+symb+"CALL%04d%02d%02d.json" %(dtdigit[2],dtdigit[0],dtdigit[1])
            fname=str(fname)
            j = json.dumps(callOIRec, indent=4)
            f = open(fname, 'w')
            print >> f, j
            f.close()
            fname="HistData/histoi/"+symb+"PUT%04d%02d%02d.json" %(dtdigit[2],dtdigit[0],dtdigit[1])
            fname=str(fname)
            j = json.dumps(putOIRec, indent=4)
            f = open(fname, 'w')
            print >> f, j
            f.close()
    except KeyboardInterrupt:
        print 'Interrupted with Ctrl-c' 
        
    dl.disconnect() 
    return rv

if __name__ == "__main__":
    preMktScan()

