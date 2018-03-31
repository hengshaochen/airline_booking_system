from flask import Flask, render_template, url_for, request, session, redirect
import bcrypt
import pymysql
from flaskext.mysql import MySQL
import sys
import datetime
import json
#import MySQLdb


app = Flask(__name__)
#app.config['MONGO_DBNAME'] = 'restaurant_pos'
#app.config['MONGO_URI'] = 'mongodb://henry:abc794613@ds111059.mlab.com:11059/restaurant_pos'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://henrychen0702:Abc794613@henrychen0702.cqdz4l9ywfoh.us-east-2.rds.amazonaws.com:3306/airlines' #这里登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名text1
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True #设置这一项是每次请求结束后都会自动提交数据库中的变动

#conn = MySQL.connect(host="henrychen0702.cqdz4l9ywfoh.us-east-2.rds.amazonaws.com:3306/airlines",user="henrychen0702",password="Abc794613",db="airlines")



@app.route('/')
def index():
	if 'username' in session:
		return render_template('dashboardUser.html')
	return render_template('index.html')

	#cur = mysql.get_db().cursor()
	#cur.execute('''SELECT * FROM account''')
	#rv = cur.fetchall()
	#return str(rv)

@app.route('/dashboardUser', methods=['POST', 'GET'])
def dashboardUser():

	print('DASHBOARD TEST!', file=sys.stderr)
	# POST
	if request.method == 'POST':
		try:
			db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
			cursor = db.cursor()

			# Get the weekday of the depart time
			dt = request.form['depeartDate']
			year, month, day = (int(x) for x in dt.split('-'))    
			# Monday = 0 , Sunday = 6
			weekday = datetime.date(year, month, day).weekday()
			weekdayLikeSearch = "%" + str(weekday) + "%"

			# check if there have enough seat
			#request.form['numberTravelers'] +
			numberTravelers = request.form['numberTravelers']
			cursor.execute('''SELECT flightNumber from Remain where numberOfSeat - soldSeat > %s ''', (request.form['numberTravelers']))
			availableFlight = cursor.fetchall()
			print(availableFlight, file=sys.stderr)
			#cursor.execute('''SELECT flightNumber from Remain where  ''')
			cursor.execute('''SELECT * from Flight where origin = %s AND destination = %s AND WorkingDay LIKE %s AND flightNumber IN %s''', (request.form['from'], request.form['to'], weekdayLikeSearch, availableFlight))

			flightInfo = cursor.fetchall()
			#print(results, file=sys.stderr)
			print(flightInfo, file=sys.stderr)
			#flightInfo = results[0][0] + results[0][1]
			#flightInfo = []
			#for x in range(0, len(results)):
			#	print(type(flightInfo))
				#print(len(results))
			#	flightInfo.append(results[x][0])
			print("testtest", file=sys.stderr)
			flightTotalPrice = []
			flightInfo_flightNumber = []
			for x in range(0, len(flightInfo)):
				flightTotalPrice.append(flightInfo[x][5] * int(numberTravelers))
				flightInfo_flightNumber.append(flightInfo[x][0])
			#print(flightTotalPrice, file=sys.stderr)

			print(type(DateTimeEncoder().encode(flightInfo[0][8])), file=sys.stderr)
			print(DateTimeEncoder().encode(flightInfo[0][8]), file=sys.stderr)

			session['flightInfo_flightNumber'] = flightInfo_flightNumber
			session['numberTravelers'] = numberTravelers
			session['flightTotalPrice'] = flightTotalPrice
			return render_template('bookFlight.html', flightInfo=flightInfo, numberTravelers=numberTravelers, flightTotalPrice=flightTotalPrice)
		except:
			return 'Register Fail! Please try again.'

	# if not POST, then it is GET
	return render_template('dashboardUser.html')


@app.route('/bookFlight', methods=['POST', 'GET'])
def bookFlight():

	print('bookFlight Test!', file=sys.stderr)
	# POST
	if request.method == 'POST':
		try:
			db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
			#cursor = db.cursor()

			totalFlight = session.get('flightInfo_flightNumber', None)
			selectFlight = int(request.form['selectFlight']) - 1
			print("AAAA",file=sys.stderr)
			print(type(totalFlight[selectFlight]), file=sys.stderr)
			print(totalFlight[selectFlight], file=sys.stderr)
			print("BBBBBB",file=sys.stderr)

			# insert field for reservation
			cursor = db.cursor()
			cursor.execute('''SELECT * FROM Reservation''')
			reservationNumber = cursor.rowcount

			Time = datetime.datetime.now()

			Passengers = request.form['passengersName']
			print("CCCC",file=sys.stderr)
			print(Passengers, file=sys.stderr)
			print("FFF",file=sys.stderr)
			
			cursor = db.cursor()
			#cursor.execute('''INSERT into Reservation (ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative) 
			#	value(%d, %s, %s, %s, %s, %s, %s)''', (rowcount, 1))
			# 查db當前有幾筆資料已獲得下一筆訂單編號
			#cursor2 = db.cursor()
			#curson2.execute('''INSERT into Schedule (FlightNumber, ReservationNumber)
            #      values (%s, %d)''',
            #      ("totalFlight[selectFlight]", 1))

			print("DDD",file=sys.stderr)
			# 提交到数据库执行
			#db.commit()

			# 把使用者選的編號的航班，訂票人數寫入Reservation
			return render_template('/dashboardUser.html')
		except:
			return 'Book Fail! Please try again.'

	# if not POST, then it is GET
	return render_template('bookFlight.html')


@app.route('/login', methods=['POST'])
def login():

	db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","airlines" )
	cursor = db.cursor()

	#sql = "select * from account where user="+request.form['username']+" AND password="+request.form['pass']+""
    
	try:
		cursor.execute('''SELECT * from account where user = %s AND password = %s''', (request.form['username'], request.form['pass']))
		results = cursor.fetchall()
		
		if len(results) == 1:
			session['username'] = request.form['username']
			if results[0][2] == 1:
				# admin
				return render_template('dashboardAdmin.html')
			else:
				# user
				return render_template('dashboardUser.html')
			#print(results[0][2], file=sys.stderr)

			#return render_template('dashboard.html', your_list=results[0][2])

		else:
			return '登入失敗，請確認您的帳號或密碼是否正確'
	except:
		return 'Fail'

    #if login_user:
    #	# 如果user存在，驗證db中的password是否跟使用者輸入的相同
    #    if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
    #        session['username'] = request.form['username']
    #        return redirect(url_for('index'))

	return 'Invalid username and password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
	db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","airlines" )
	if request.method == 'POST':
		cur = db.cursor()
		#sql = "INSERT INTO account(user, password) VALUES (" + request.form['username'] + "," + request.form['pass'] + ")"
		#sql = "INSERT INTO account(user, password) VALUES ("+request.args.get('user')+", "+request.args.get('password')+")"

		#sql = "INSERT INTO account(user, password) VALUES ("+request.form['username']+", "+request.form['password']+")"
		try:
	        # 执行sql语句
			#cur.execute(sql)
			#hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())

			cur.execute('''INSERT into account (user, password)
                  values (%s, %s)''',
                  (request.form['username'], request.form['pass']))

			# 提交到数据库执行
			db.commit()
			#注册成功之后跳转到登录页面
			return render_template('index.html')
		except:
			return 'Register Fail! Please try again.'

	# if not POST, then it is GET
	return render_template('register.html')



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