# -*- coding: utf-8 -*-
#compute pivots from CSV file

import math as mth
import os.path, time
from collections import OrderedDict
import IbHistDataCSV as hD

def PivotsCSV(symb,sec='stk'):
	fileName = hD.genFileName(symb,sec,'1_day')
	if os.path.isfile(fileName)==False: # no such file 
		print "File does not exist!"
		return [-1,-1,-1,-1,-1,-1,-1]
		
	file = open(fileName, 'r')
	Data = file.readlines()
	file.close()
	lastRow = Data[-1]
	rec=lastRow.split(",")
	print "calculating pivots of ",symb, "from CSV data updated on ", rec[0],"/",rec[1],"/",rec[2]

	P =(float(rec[7])+float(rec[8])+float(rec[9]))/3
	#P = (H + L + C) / 3
	#P = (H + L + C + C) / 4
	#P = (H + L + O + O) / 4
	R1 = 2*P-float(rec[8])
	S1 = 2*P-float(rec[7])
	M=float(rec[7])-float(rec[8])
	R2 = P+M
	S2 = P-M
	R3 = R1+M
	S3 = S1-M
	return [round(R3,2),round(R2,2),round(R1,2),round(P,2),round(S1,2),round(S2,2),round(S3,2)]