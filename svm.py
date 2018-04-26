from sklearn import linear_model
import numpy as np
from sklearn.svm import LinearSVR
from flaskext.mysql import MySQL
import pymysql
from data import Spider

conn = pymysql.connect(host='class568.cgzotjrssahz.us-east-1.rds.amazonaws.com', user='ryan', passwd='11111111', db='stock')



def BayesianEstimate(X, Y, index, volume):
	clf = linear_model.BayesianRidge()
	clf.fit(X, Y)
	# # print Y
	# length = len(Y)
	result = clf.predict([[index, volume]])
	return result[0]
	
def SvmEstimate(X,index):
	train_len = 40
	if index < train_len + 10:
		return X[index]
	X_train = []
	y_train = []
	for i in range(index - train_len, index):
		X_train.append(X[i - 10:i])
		y_train.append(X[i])
	regr = LinearSVR()
	regr.fit(X_train,y_train)
	X_New = X[index-10:index]
	return regr.predict([X_New])[0]


# def predict(indexVolume, price, number):
# 	newIndexVolume = []
# 	newPrice = []
# 	for i in range(number - 1):
# 		newIndexVolume.append(indexVolume[i])
# 		newPrice.append(price[i])

# 	return BayesianEstimate(newIndexVolume, newPrice, indexVolume[number][1])

def historyPredictor(stockName, type):
	cursor = conn.cursor()
	value = [stockName]
	timePriceVolume = []
	if type == 'historical':
		cursor.execute("SELECT historyTime, closePrice, volume FROM HistoryPrice WHERE symbol=%s", value)
		timePriceVolume = cursor.fetchall()
	elif type == 'realtime':
		spider = Spider()
		spider.run_ten_real()
		timePriceVolume = spider.predictData[stockName]
	print("Length = ", len(timePriceVolume))

	# The five column is index, openPrice, highPrice, lowPrice and volume.
	# This is used for training.
	indexVolume = []
	for i in range(len(timePriceVolume)):
		indexVolume.append([i + 1, timePriceVolume[i][2]])
	# This array stores the actual prices of this stock of whole year.
	price = []
	new_price = []
	for i in range(len(timePriceVolume)):
		price.append([timePriceVolume[i][1]])
		new_price.append(timePriceVolume[i][1])

	window = []
	tenPrice = []
	for i in range(10):
		window.append([i + 1, timePriceVolume[i][2]])
		tenPrice.append([timePriceVolume[i][1]])

	res = []
	for i in range(10):
		res.append([timePriceVolume[i][0].__str__(), price[i][0], price[i][0]])
	

	for i in range(10, len(timePriceVolume)):
		print(i)
		# res.append([timePriceVolume[i][0].__str__(), price[i][0], BayesianEstimate(window, tenPrice, i, timePriceVolume[i][2])])
		res.append([timePriceVolume[i][0].__str__(), price[i][0], SvmEstimate(new_price, i)])
		if i != len(timePriceVolume) - 1:
			window.pop(0)
			window.append([i + 2, timePriceVolume[i + 1][2]])
			tenPrice.pop(0)
			tenPrice.append([timePriceVolume[i + 1][1]])

	return res

# Test functions.
def main():
	res = historyPredictor('GOOG');
	# for i in range(len(res)):
	# 	print('{0} {1} {2}'.format(res[i][0], res[i][1], res[i][2]))
	print(res)
	
if __name__ == '__main__':
	main()