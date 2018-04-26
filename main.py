from flask import Flask, render_template, url_for, request, session, redirect, flash, json, jsonify, Response
import bcrypt
import pymysql
from flaskext.mysql import MySQL
import sys
import datetime
import json
import time
import bcf, svm, rnn, realTime, indicator
from flask_restful import Resource, Api, reqparse
from data import Spider


app = Flask(__name__)
api = Api(app)

spider = Spider()

# RestFUL API
# class HelloWorld(Resource):
# 	def get(self):
# 		return {'about' : 'Hello'}

# class Multi(Resource):
# 	def get(self, num, num2):
# 		return {'result': num * num2 * 10}

def myconverter(o):
	if isinstance(o, datetime.date):
		return o.__str__()


class fetchStockPrice(Resource):
	def get(self):
		stockTicker = request.args['stockTicker']
		historical = request.args['historical']
		print(stockTicker)
		print(historical)
		if historical == "true":
			db = pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com","ryan","11111111","stock" )
			cursor = db.cursor()
			cursor.execute('''SELECT historyTime, closePrice from HistoryPrice''')
			results = cursor.fetchall()
			print (results)

			return {'results': json.dumps(results, default = myconverter)}

		else:
			print("else")

		return {'stockTicker': stockTicker, 'historical': historical}


class fetchStockPrice2(Resource):
	def get(self):
		stockTicker = request.args['stockTicker']
		historical = request.args['historical']
		print("price2")
		print(stockTicker)
		print(historical)
		if historical == "true":
			db = pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com","ryan","11111111","stock" )
			cursor = db.cursor()

			lists = predictor.historyPredictor(stockTicker)

			print(lists)
			resp = Response('dashboardUser.html', mimetype='text/html')
			return resp
			#return render_template('query_and_predict.html', lists=json.dumps(lists))

		else:
			print("else")

		# return {'stockTicker': stockTicker, 'historical': historical}

api.add_resource(fetchStockPrice, '/fetchStockPrice')
api.add_resource(fetchStockPrice2, '/fetchStockPrice2')
#api.add_resource(HelloWorld, '/')
#api.add_resource(Multi, '/multi/<int:num>/<int:num2>')

@app.route('/')
def index():
	if 'username' in session:
		companyName = ['GOOG','AABA','VMW','BABA','HPQ','AAPL','AMZN','FB','IBM','SNAP']
		dictReal = dict()
		for i in range(len(companyName)):
			spider.run_one_real(companyName[i])

		for key in spider.showdata:
			dictReal[key] = round(spider.showdata[key][-1][1], 2)
		#print(spider.showdata)
		#print(spider.showdata['FB'])
		return render_template('dashboardUser.html', dictReal=dictReal)
	return render_template('index.html')

# @app.route('/test/<int:num>', methods=['GET'])
# def multi_10(num):
# 	return jsonify({"ans:": num*10})

@app.route('/dashboardUser', methods=['POST', 'GET'])
def dashboardUser():

	print('dashBoard User', file=sys.stderr)
	# POST
	if request.method == 'GET':
		try:
			db = pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com","ryan","11111111","stock" )
			cursor = db.cursor()

			stock_name = request.args['stock_name']
			select_date = request.args['select_date']
			history_or_today = request.args['history_or_today']
			predictor = request.args['predictor']
			print("test dashBoard")
			print("stock name:", stock_name)
			cursor.execute('''SELECT historyTime, closePrice from HistoryPrice where historyTime < %s''', (select_date))
			results = cursor.fetchall()

			#lists = predictor.historyPredictor(stock_name)
			#lists = svm.historyPredictor(stock_name)
			if history_or_today == "1":
				if predictor == "1":
					print("aa")
					print(stock_name)
					lists = bcf.historyPredictor(stock_name, "historical")
					print("bb")
				elif predictor == "2":
					lists = svm.historyPredictor(stock_name, "historical")
				else:
					lists = rnn.historyPredictor(stock_name, "historical")

				print("CD")
				cursor.execute('''SELECT max(highPrice) from HistoryPrice where symbol = %s order by historyTime desc limit 10''', [stock_name])
				print("EF")
				highest = cursor.fetchall()[0][0]
				print(highest)
				cursor.execute('''SELECT avg(highPrice) from HistoryPrice where symbol = %s order by historyTime desc limit 10''', [stock_name])
				average = cursor.fetchall()[0][0]
				cursor.execute('''SELECT min(highPrice) from HistoryPrice where symbol = %s order by historyTime desc limit 10''', [stock_name])
				lowest = cursor.fetchall()[0][0]

				cursor.execute('''select symbol from (select symbol as symbol, avg(highPrice) as avgPrice from HistoryPrice where symbol != %s group by symbol) as A where A.avgPrice < (select min(lowPrice) as minPrice from HistoryPrice where symbol = %s)''', [stock_name, stock_name])
				ans_res = cursor.fetchall()
				
				print(average)
				print(lowest)
				print(ans_res)
				return render_template('query_and_predict.html', lists=json.dumps(lists), history_or_today=history_or_today
					, stock_name=stock_name, highest=highest, average=average, lowest=lowest, ans_res=ans_res)
			else:
				# realTime
				print("test2")
				list = None
				if predictor == "1":
					print("aa")
					print(stock_name)
					lists = bcf.historyPredictor(stock_name, "realtime")
					print("bb")
				elif predictor == "2":
					lists = svm.historyPredictor(stock_name, "realtime")
					print("CCCC", type(lists[0][2]))
				else:
					lists = rnn.historyPredictor(stock_name, "realtime")
				
				print("listtype:", type(lists[0][0]))

				# lists = realTime.show()
				##spider.run_one_real(stock_name)
				##realTime_dict = spider.showdata
				##lists = realTime_dict[stock_name]
				##print(realTime_dict)
				#print(realTime_dict['FB'])
				return render_template('query_realTime.html', lists=json.dumps(lists))



		#except Exception as e: print(e)
		except:
			return 'Fail'

	# if not POST, then it is GET
	return render_template('dashboardUser.html')

@app.route('/indicatorPage', methods=['POST', 'GET'])
def indicatorPage():

	print('indicatorPage', file=sys.stderr)
	# POST
	if request.method == 'GET':
		try:
			stock_name = request.args['stock_name']
			indicatorSelect = request.args['indicatorSelect']
			#lists = None
			if indicatorSelect == "1":
				lists = indicator.MTM(stock_name)
				return render_template('indicatorPage.html', lists=json.dumps(lists), indicatorSelect="MTM")
			elif indicatorSelect == "2":
				lists = indicator.RSI(stock_name)
				return render_template('indicatorPage.html', lists=json.dumps(lists), indicatorSelect="RSI")
			else:
				lists = indicator.MACD(stock_name)
				return render_template('macdIndicator.html', lists=json.dumps(lists), indicatorSelect="MACD")

		#except Exception as e: print(e)
		except:
			return 'Fail'

	# if not POST, then it is GET
	return render_template('dashboardUser.html')




@app.route('/queryDetail', methods=['POST', 'GET'])
def queryDetail():

	print('queryDetail', file=sys.stderr)
	# POST
	if request.method == 'GET':
		try:
			stock_name = request.args['stock_name']
			select_date = request.args['select_date']

			db = pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com","ryan","11111111","stock" )
			cursor = db.cursor()
			cursor.execute('''SELECT * from HistoryPrice where historyTime = %s AND symbol = %s''', (select_date, stock_name))	
			
			#symbol, historyTime, openPrice, highPrice, lowPrice, closePrice, volume
			results = cursor.fetchall()[0]

			openPrice = results[2]
			highPrice = results[3]
			lowPrice = results[4]
			closePrice = results[5]
			volume = results[6]
			####
			#lists = None
			return render_template('queryDetail.html', stock_name=stock_name, select_date=select_date,
				openPrice=openPrice, highPrice=highPrice, lowPrice=lowPrice, closePrice=closePrice, volume=volume)


		#except Exception as e: print(e)
		except:
			return 'Fail'

	# if not POST, then it is GET
	return render_template('dashboardUser.html')


@app.route('/query_and_predict', methods=['POST', 'GET'])
def query_and_predict():

	print('query_and_predict page', file=sys.stderr)
	# POST
	if request.method == 'POST':
		try:
			print("test query and predict")
		except:
			return 'Dashboard Fail! Please try again.'

	# if not POST, then it is GET
	print("vvvv")
	return render_template('dashboardUser.html')


@app.route('/dashboardAdmin', methods=['POST', 'GET'])
def dashboardAdmin():
	print("test admin")



@app.route('/login', methods=['POST'])
def login():

	db = pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com","ryan","11111111","stock" )
	cursor = db.cursor()

	try:
		cursor.execute('''SELECT * from ACCOUNT where username = %s AND pass = %s''', (request.form['username'], request.form['pass']))
		results = cursor.fetchall()
		
		if len(results) == 1:
			print("A")
			session['username'] = request.form['username']
			session['AccountNumber'] = results[0][0]
			print("B")
			print(results[0][2] == 0)
			if results[0][2] == 1:
				# admin
				return render_template('dashboardAdmin.html')
			else:
				# user
				return render_template('dashboardUser.html')
		else:
			return 'Login Fail, please double check your username or password'
	except:
		return 'Fail'

	return 'Invalid username and password combination'

@app.route('/logout', methods=['GET'])
def logout():
   if 'username' in session:
      # remove the username from the session if it's there
      #session.pop('username', None)
      session.clear()
      return render_template('index.html')

   # except:
   #     return 'Fail to log out'

@app.route('/register', methods=['POST', 'GET'])
def register():
   db = pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com","ryan","11111111","stock" )
   if request.method == 'POST':
      cur = db.cursor()
      try:
         cur.execute('''SELECT * FROM ACCOUNT''')
         totalNumber = cur.rowcount
         sql_Account = "insert into ACCOUNT values('%s', '%s', 0)"%(request.form['username'], request.form['pass'])
         cur.execute(sql_Account)
         db.commit()
         return render_template('index.html')
      except:
         return 'Register Fail! Please try again.'

   # if not POST, then it is GET
   return render_template('register.html')


def cal_discount(date1, date2):
	print("Enter the func")
	days = abs((date2-date1).days)
	print(days)
	if days - 21 >= 0:
		return 0.7
	elif days -14 >= 0:
		return 0.8
	elif days - 7 >= 0:
		return 0.9
	else:
		return 1.0


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        else:
            return super(DateTimeEncoder, self).default(obj)

if __name__ == '__main__':
	app.secret_key = 'mysecret'
	app.run(debug=True)