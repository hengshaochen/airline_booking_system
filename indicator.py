import pymysql

#MTM_num=10
#MTM_mean_num=10
#RSI_num=14
#DIF_fn=12
#DIF_sn=26
#DEM_n=9

#MTM_num=10
#MTM_mean_num=10
#RSI_num=14
#DIF_fn=12
#DIF_sn=26
#DEM_n=9

stock="GOOG"

#connect db
times=0
N=10
while (times<N):
	try:
		db=pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com","ryan","11111111","stock")
		break
	except:
		times+=1

#indicator MTM
def MTM(stock):
	num=10
	mean=10
	data=[]
	#rt="select closePrice from HistoryPrice where symbol="+stock+" order by historyTime desc limit %s;" %(num+mean+2)
	rt="select closePrice, historyTime from HistoryPrice where symbol='"+stock+"' order by historyTime desc"
	try:
		cursor=db.cursor()
		cursor.execute(rt)
		resultrt=cursor.fetchall()
		print(resultrt)
		for row in resultrt:
			data.append(row)
		cursor.close()
	except:
		db.rollback()
	MTM_data=[]
	res=[]
	for i in range(len(data)-num):
		MTM_data.append(float(data[i+num][0])-float(data[i][0]))
	MTM_sum=0
	for i in range(mean):
		MTM_sum+=MTM_data[i]
	res.append([data[0][1].__str__(), float(MTM_sum)/float(mean)])
	for i in range (1,len(MTM_data)-mean):
		MTM_sum=MTM_sum-MTM_data[i-1]+MTM_data[i+mean-1]
		res.append([data[i][1].__str__(), float(MTM_sum)/float(mean)])
	res.reverse()
	return res
	# if MTM_yd<0 and MTM_td>0:
	# 	return "buy"
	# if MTM_yd>0 and MTM_td<0:
	# 	return "sell"

#indicator RSI
def RSI(stock):
	num=14
	data=[]
	#rt="select closePrice from HistoryPrice where symbol="+stock+" order by historyTime desc limit %s;" %(num+1)
	rt="select closePrice, historyTime from HistoryPrice where symbol='"+stock+"' order by historyTime desc"
	try:
		cursor=db.cursor()	
		cursor.execute(rt)
		resultrt=cursor.fetchall()
		for row in resultrt:
			data.append(row)
		cursor.close()
	except:
		db.rollback()
	data.reverse()
	U=[]
	D=[]
	for i in range (len(data)-1):
		if data[i+1][0]<data[i][0]:
			D.append(data[i][0]-data[i+1][0])
			U.append(0)
		else:
			U.append(data[i+1][0]-data[i][0])
			D.append(0)
	alpha=float(1)/float(num)
	res=[]
	for i in range (num-1,len(data)-1):
		RS_U=U[i-num+1]
		RS_D=D[i-num+1]
		for j in range (num-1):
			RS_U=alpha*U[i-num+1+j+1]+(1-alpha)*RS_U
			RS_D=alpha*D[i-num+1+j+1]+(1-alpha)*RS_D
		RS=RS_U/RS_D
		RSI=100-100/(1+RS)
		res.append([data[i+1][1].__str__(),RSI])
	return res
	# if RSI<=30:
	# 	return "Oversold,buy"
	# if RSI>=70:
	# 	return "Overbought,sell"

#indicator MACD
def MACD(stock):
	fn=12
	sn=26
	num=9
	data=[]
	DIF=[]
	DEM=[]
	#rt="select closePrice from HistoryPrice where symbol="+stock+" order by historyTime desc limit %s;" %(sn+num+1)
	rt="select closePrice, historyTime from HistoryPrice where symbol='"+stock+"' order by historyTime desc"
	try:
		cursor=db.cursor()	
		cursor.execute(rt)
		resultrt=cursor.fetchall()
		for row in resultrt:
			data.append(row)
		cursor.close()
	except:
		db.rollback()
	data.reverse()
	#RES is [data,DIF,DEM]
	res=[]
	for i in range (sn+num-2,len(data)):
		for j in range (num):
			EMA_fn=data[i-fn-num+2+j][0]
			for k in range (fn-1):
				EMA_fn=(1-float(2)/(float(fn)+1))*EMA_fn+(float(2)/(float(fn)+1))*data[i-fn-num+3+j+k][0]
			EMA_sn=data[i-sn-num+2+j][0]
			for k in range (sn-1):
				EMA_sn=(1-float(2)/(float(sn)+1))*EMA_sn+(float(2)/(float(sn)+1))*data[i-sn-num+3+j+k][0]
			DIF=EMA_fn-EMA_sn
			if j==0:
				DEM=DIF
			else:
				DEM=(1-float(2)/(float(num)+1))*DEM+(float(2)/(float(num)+1))*DIF
		res.append([data[i][1].__str__(),DIF,DEM])
	return res
	#for i in range (len(DEM)):
	#	res.append()
	# if DIF[1]<DEM_yd and DIF[0]>DEM_td:
	# 	return "buy"
	# if DIF[1]>DEM_yd and DIF[0]<DEM_td:
	# 	return "sell"
		

#MTM_result=MTM(stock)
#print MTM_result
#RSI_result=RSI(stock)
#print RSI_result
#MACD_result=MACD(stock)
#print MACD_result