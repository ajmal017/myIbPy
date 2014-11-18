import time
from getPrevDayStat import getPrevDayStat
from techStat.SMA import SMA
from techStat.PivotsCSV import PivotsCSV
import operator

def prt(pt):
	htmlDict={0:"#ff0000",1:"#e06666",2:"#f6b26b",3:"#a2c4c9",4:"#6fa8dc",5:"#0b5394",6:"#351c75",7:'200',8:'100',9:'50',10:'20'}
	if pt[0]<7:
		s='''<td><font color="%s">%.1f</font></td>''' %(htmlDict[pt[0]],pt[1])
	else:
		s='''<td>%.1f<sup>%s</sup></td>'''%(pt[1],htmlDict[pt[0]])
	return s

def generateHTML(contractDict,numSMA,pv,premkt):
	
	keyDict = {0:'R3',1:'R2',2:'R1',3:'Pivot',4:'S1',5:'S2',6:'S3',7:'200',8:'100',9:'50',10:'20'}
	prlist={}
	for i in range(0,len(contractDict)):
		tmpdict={}
		for j in range(0,7):
			tmpdict[j]=pv[i][j]
		for j in range(7,11):
			tmpdict[j]=numSMA[i][j-7]
		prlist[i]=sorted(tmpdict.iteritems(), key=operator.itemgetter(1),reverse=True)
		

	htmlstr='''<html:div xmlns:html="http://www.w3.org/1999/xhtml">'''
	
	for line in premkt:
		htmlstr+=line

	htmlstr+='''
		<p><b>Daily Cheat Sheet</b></p>
        '''
	htmlstr+='''
        <table style="width:300px">
		<tr>'''
	for i in range(0,len(contractDict)):
		htmlstr+='<td>%s</td>' %contractDict[i][0]
	
	htmlstr+='''</tr>
		'''
	for j in range(0,len(keyDict)):
		htmlstr+='''
        <tr>'''
		for i in range(0,len(contractDict)):
			htmlstr+=prt(prlist[i][j])
		htmlstr+='''</tr>
                    '''
	tm=time.asctime()
	htmlstr+='''
        </table>
		<div>
		<p>updated on %s </p>
		</div>
		</html:div>''' % tm
		
	print 'HTML generated!'
	return str(htmlstr)

if __name__ == "__main__":
	print generateHTML(contractDict={0:['TSLA','STK'],1:['SCTY','STK']},
					   numSMA={0:[115,120,113,140],1:[15,20,13,40]},pv={0:[151,147,139,131,123,117,110],1:[48,47,39,31,23,17,16]},premkt=' ')