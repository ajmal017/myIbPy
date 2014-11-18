#!/usr/bin/python

import urllib2
from time import sleep

def readPv(sym):
    url = "http://www.barchart.com/cheatsheet.php?sym="+sym
    content = urllib2.urlopen(url).read()
    
    chartbg=content.find('Pivot Point 2nd Level Resistance')
    content=content[chartbg:]
    chartend=content.find('\n')
    content=content[0:chartend]
    
    pR2=content.find('<div class="">')
    content=content[pR2+len('<div class="">'):]
    pR2=content.find('</div>')
    
    R2=float(content[0:pR2])
    
    pR1=content.find('Pivot Point 1st Level Resistance')
    content=content[pR1:]
    
    pR1=content.find('<div class="">')
    content=content[pR1+len('<div class="">'):]
    pR1=content.find('</div>')
    
    R1=float(content[0:pR1])
    
    pPv=content.find('Pivot Point')
    pcontent=content[:pPv]
    content=content[pPv:]
    
    pPv=pcontent.rfind('<div class="">')
    pcontent=pcontent[pPv+len('<div class="">'):]
    pPv=pcontent.find('</div>')
    
    Pv=float(pcontent[0:pPv])
    
    pS1=content.find('Pivot Point 1st Level Support')
    content=content[pS1:]
    
    pS1=content.find('<div class="">')
    content=content[pS1+len('<div class="">'):]
    pS1=content.find('</div>')
    
    S1=float(content[0:pS1])
    
    pS2=content.find('Pivot Point 2nd Level Support')
    content=content[pS1:]
    
    pS2=content.find('<div class="">')
    content=content[pS2+len('<div class="">'):]
    pS2=content.find('</div>')
    
    S2=float(content[0:pS2])
    

    return [R2,R1,Pv,S1,S2]

    #    result = json.loads(content)
    #if result['status'] != 'OK':
    #    print 'get error'
#    return
#print 'FROM: ' + result['origin_addresses'][0]

if __name__ == '__main__':
    print readPv('SCTY')
    sleep(10)
    print readPv('TSLA')


