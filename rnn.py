import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing
import pymysql
import keras
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from data import Spider
conn = pymysql.connect(host='class568.cgzotjrssahz.us-east-1.rds.amazonaws.com', user='ryan', passwd='11111111', db='stock')

### The function below transforms the input series and window-size into a set of input/output pairs for our RNN model
def window_transform_series(series,window_size):
    # containers for input/output pairs
    X = []
    y = []
    
    for i in range(window_size, len(series)):
        X.append(series[i - window_size:i])
        y.append(series[i])
        
        
    # reshape each 
    X = np.asarray(X)
    X.shape = (np.shape(X)[0:2])
    y = np.asarray(y)
    y.shape = (len(y),1)
    
    return X,y

def historyPredictor(stockName, type):
	if type == 'historical':
		# take out close price and volume from table and store them into array.
		cursor = conn.cursor()
		value = [stockName]
		cursor.execute("SELECT closePrice FROM HistoryPrice WHERE symbol=%s", value)
		# The first column of priceAndVolume is close price, second column is volume.
		#dbdata = cursor.fetchall();
		#dbdata = np.fromiter(cursor.fetchall(), float)

		# convert the mysql data to numpy array
		dataCopy = np.array(cursor.fetchall(),dtype=float)
		
		# Normalize to [0,1]
		#dataset = dataCopy
		dataset = dataCopy / dataCopy.max(axis=0)


		# And now we can window the data using our windowing function
		window_size = 7
		X,y = window_transform_series(series = dataset,window_size = window_size)


		# split train and testing sets
		train_test_split = int(np.ceil(2*len(y)/float(3)))   # set the split point
		##print(train_test_split)
		# partition the training set
		X_train = X[:train_test_split,:]
		y_train = y[:train_test_split]

		##print(len(X_train))
		##print(len(y_train))

		# keep the last chunk for testing
		X_test = X[train_test_split:,:]
		y_test = y[train_test_split:]
		##print(len(X_test))
		##print(len(y_test))

		# NOTE: to use keras's RNN LSTM module our input must be reshaped to [samples, window size, stepsize] 
		X_train = np.asarray(np.reshape(X_train, (X_train.shape[0], window_size, 1)))
		X_test = np.asarray(np.reshape(X_test, (X_test.shape[0], window_size, 1)))

		##print(X_train)

		# build the RNN model
		# start with fixed random seed
		np.random.seed(0)


		# Build an RNN to perform regression on our time series input/output data
		model = Sequential()
		model.add(LSTM(5, input_shape=(window_size, 1)))
		model.add(Dense(1))

		optimizer = keras.optimizers.RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)

		# compile the model
		model.compile(loss='mean_squared_error', optimizer=optimizer)

		model.fit(X_train, y_train, epochs=500, batch_size=64, verbose=1)
		#print(X)


		# generate predictions for training
		train_predict = model.predict(X_train)
		test_predict = model.predict(X_test)
		#print(dataCopy.max(axis=0))


		#cc = train_predict * np.linalg.norm(dataCopy)
		train_predict_denormalize = train_predict * dataCopy.max(axis=0)
		test_predict_denormalize = test_predict * dataCopy.max(axis=0)

		predict_result = []
		#result = np.concatenate(train_predict_denormalize, test_predict_denormalize)
		for i in range(len(train_predict_denormalize)):
			predict_result.append(train_predict_denormalize[i][0])
		for i in range(len(train_predict_denormalize), len(train_predict_denormalize) + len(test_predict_denormalize)):
			predict_result.append(test_predict_denormalize[len(train_predict_denormalize) - i][0])

		##print(len(predict_result))
		cursor.execute("SELECT historyTime, closePrice FROM HistoryPrice WHERE symbol=%s", value)
		timePriceVolume = cursor.fetchall()

		res = []

		res = []
		for i in range(7):
			res.append([timePriceVolume[i][0].__str__(), timePriceVolume[i][1], timePriceVolume[i][1]])

		for i in range(7, len(timePriceVolume)):
			res.append([timePriceVolume[i][0].__str__(), timePriceVolume[i][1], predict_result[i - 7]])

		##print(len(res))
		return res
	elif type == 'realtime':
		print("00")
		spider  = Spider()
		print("aa")
		spider.run_ten_real()
		print("bb")
		timePriceVolume = spider.predictData[stockName]
		print("cc")
		# take out close price and volume from table and store them into array.

		# cursor = conn.cursor()
		# value = [stockName]
		# cursor.execute("SELECT closePrice FROM HistoryTime WHERE symbol=%s", value)

		# The first column of priceAndVolume is close price, second column is volume.
		#dbdata = cursor.fetchall();
		#dbdata = np.fromiter(cursor.fetchall(), float)

		closePriceArray = [x[1] for x in timePriceVolume]
		# convert the mysql data to numpy array
		dataCopy = np.array(closePriceArray,dtype=float)
		
		# Normalize to [0,1]
		#dataset = dataCopy
		dataset = dataCopy / dataCopy.max(axis=0)


		# And now we can window the data using our windowing function
		window_size = 7
		X,y = window_transform_series(series = dataset,window_size = window_size)


		# split train and testing sets
		train_test_split = int(np.ceil(2*len(y)/float(3)))   # set the split point
		##print(train_test_split)
		# partition the training set
		X_train = X[:train_test_split,:]
		y_train = y[:train_test_split]

		##print(len(X_train))
		##print(len(y_train))

		# keep the last chunk for testing
		X_test = X[train_test_split:,:]
		y_test = y[train_test_split:]
		##print(len(X_test))
		##print(len(y_test))

		# NOTE: to use keras's RNN LSTM module our input must be reshaped to [samples, window size, stepsize] 
		X_train = np.asarray(np.reshape(X_train, (X_train.shape[0], window_size, 1)))
		X_test = np.asarray(np.reshape(X_test, (X_test.shape[0], window_size, 1)))

		##print(X_train)

		# build the RNN model
		# start with fixed random seed
		np.random.seed(0)


		# Build an RNN to perform regression on our time series input/output data
		model = Sequential()
		model.add(LSTM(5, input_shape=(window_size, 1)))
		model.add(Dense(1))

		optimizer = keras.optimizers.RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)

		# compile the model
		model.compile(loss='mean_squared_error', optimizer=optimizer)

		model.fit(X_train, y_train, epochs=100, batch_size=64, verbose=1)
		#print(X)


		# generate predictions for training
		train_predict = model.predict(X_train)
		test_predict = model.predict(X_test)
		#print(dataCopy.max(axis=0))


		#cc = train_predict * np.linalg.norm(dataCopy)
		train_predict_denormalize = train_predict * dataCopy.max(axis=0)
		test_predict_denormalize = test_predict * dataCopy.max(axis=0)

		predict_result = []
		#result = np.concatenate(train_predict_denormalize, test_predict_denormalize)
		for i in range(len(train_predict_denormalize)):
			predict_result.append(train_predict_denormalize[i][0])
		for i in range(len(train_predict_denormalize), len(train_predict_denormalize) + len(test_predict_denormalize)):
			predict_result.append(test_predict_denormalize[len(train_predict_denormalize) - i][0])

		##print(len(predict_result))
		# cursor.execute("SELECT historyTime, closePrice FROM HistoryPrice WHERE symbol=%s", value)
		timePrice = [[x[0], x[1]] for x in timePriceVolume]

		res = []

		res = []
		for i in range(7):
			res.append([timePrice[i][0].__str__(), timePrice[i][1], timePrice[i][1]])

		for i in range(7, len(timePrice)):
			res.append([timePrice[i][0].__str__(), timePrice[i][1], predict_result[i - 7]])

		##print(len(res))
		#print(res)
		return res

