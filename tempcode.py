	qtype = "nada"
	if msg.field == 1:
		qtype = "bid"
		priceDict[contractDict[msg.tickerId][0]][qtype]=msg.price
	if msg.field == 2:
		qtype = "ask"
		priceDict[contractDict[msg.tickerId][0]][qtype]=msg.price
	if msg.field == 4:
		qtype = "last"
		priceDict[contractDict[msg.tickerId][0]][qtype]=msg.price
	if msg.field == 9:
		qtype = "close"
		priceDict[contractDict[msg.tickerId][0]][qtype]=msg.price
	
	if qtype != "nada":
		optstring = ""
			#if float(contractDict[msg.tickerId][5]) > 0.001:
		optlist = []
		optlist.append(str(contractDict[msg.tickerId][4]))
		optlist.append(" ")
		optlist.append(str(contractDict[msg.tickerId][5]))
		optlist.append(" ")
		optlist.append(contractDict[msg.tickerId][6])
		optstring = ''.join([s for s in optlist])
		print '%s: %s: %s: %s: %s' % (contractDict[msg.tickerId][1],
									  contractDict[msg.tickerId][0], optstring, qtype, msg.price)
									  
		if contractDict[msg.tickerId][0]=='GTAT' and float(priceDict['GTAT']['last'])>=19.9 and priceListener.GTAToptExcuted == False:
			#sell GTAT option
			#contractDict[9] = ('SCTY', 'OPT', 'SMART', 'USD', '20150116', 80.0, 'CALL')
			tempOrdId=nextOrderId.orderId
			GTAToptContr=mkContract('GTAT', 'OPT', 'SMART', 'USD', '20150116', 20.0, 'CALL')
			
			lmtprice=(float(priceDict[11]['ask'])+float(priceDict[11]['bid']))/2
			print lmtprice
			GTAToptOrder = mkOrder(nextOrderId.orderId,-10, '4.0','U8852701')
			tws.placeOrder(nextOrderId.orderId, GTAToptContr, GTAToptOrder)
			priceListener.GTAToptExcuted=True

	#buy tsla option if stock price approaches SMA120
	if contractDict[msg.tickerId][0]=='TSLA':
		if priceDict[2]['last']<numSMA[3][0]+0.5:
			print "buy tsla option"
	#tempOrdId=nextOrderId.orderId
	#sctyContract = mkContract('SCTY')
	#sctyOrder = mkOrder(nextOrderId.orderId,100, '1.0')#buy scty option if stock price approaches 60, i.e. SMA200	