from sklearn import linear_model
import pymysql
from flaskext.mysql import MySQL
from data import Spider
conn = pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com","ryan","11111111","stock" )

def BayesianEstimate(X, Y, index, volume):
	clf = linear_model.BayesianRidge();
	clf.fit(X, Y)
	# # print Y
	# length = len(Y)
	result = clf.predict([[index, volume]])
	return result[0]

def historyPredictor(stockName, type):
	# if type == 'historical':
	# take out close price and volume from table and store them into array.
	cursor = conn.cursor()
	value = [stockName]
	timePriceVolume = []
	if type == 'historical':
		cursor.execute("SELECT historyTime, closePrice, volume FROM HistoryPrice WHERE symbol=%s", value)
		timePriceVolume = cursor.fetchall()
		print(timePriceVolume)
	elif type == 'realtime':
		spider  = Spider()
		spider.run_ten_real()
		timePriceVolume = spider.predictData[stockName]
	# The first column of priceAndVolume is close price, second column is volume.

	# The five column is index, openPrice, highPrice, lowPrice and volume.
	# This is used for training.
	indexVolume = []
	for i in range(len(timePriceVolume)):
		indexVolume.append([i + 1, timePriceVolume[i][2]])
	# This array stores the actual prices of this stock of whole year.
	price = []
	for i in range(len(timePriceVolume)):
		price.append([timePriceVolume[i][1]])
	cursor.close()

	window = []
	tenPrice = []
	for i in range(10):
		window.append([i + 1, timePriceVolume[i][2]])
		tenPrice.append([timePriceVolume[i][1]])

	res = []
	for i in range(10):
		if type == 'historical':
			res.append([timePriceVolume[i][0].__str__(), price[i][0], price[i][0]])
		elif type == 'realtime':
			res.append([timePriceVolume[i][0], price[i][0], price[i][0]])
	for i in range(10, len(timePriceVolume)):
		if type == 'historical':
			res.append([timePriceVolume[i][0].__str__(), price[i][0], BayesianEstimate(window, tenPrice, i, timePriceVolume[i][2])])
		elif type == 'realtime':
			res.append([timePriceVolume[i][0], price[i][0], BayesianEstimate(window, tenPrice, i, timePriceVolume[i][2])])
		if i != len(timePriceVolume) - 1:
			window.pop(0)
			window.append([i + 2, timePriceVolume[i + 1][2]])
			tenPrice.pop(0)
			tenPrice.append([timePriceVolume[i + 1][1]])

	return res