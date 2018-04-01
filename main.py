from flask import Flask, render_template, url_for, request, session, redirect
import bcrypt
import pymysql
from flaskext.mysql import MySQL
import sys
import datetime
import json
import time
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
			print(dt)
			year, month, day = (int(x) for x in dt.split('-')) 
			# Monday = 0 , Sunday = 6
			weekday = datetime.date(year, month, day).weekday()
			weekdayLikeSearch = "%" + str(weekday) + "%"

			# check if there have enough seat
			#request.form['numberTravelers'] +
			numberTravelers = request.form['numberTravelers']
			cursor.execute('''SELECT flightNumber from Remain where numberOfSeat - soldSeat >= %s ''', (request.form['numberTravelers']))
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
			flightDepart = []
			flightDestin = []
			for x in range(0, len(flightInfo)):
				flightTotalPrice.append(flightInfo[x][5] * int(numberTravelers))
				flightInfo_flightNumber.append(flightInfo[x][0])
				flightDepart.append(flightInfo[x][6])
				flightDestin.append(flightInfo[x][7])
			#print(flightTotalPrice, file=sys.stderr)

			print(type(DateTimeEncoder().encode(flightInfo[0][8])), file=sys.stderr)
			print(DateTimeEncoder().encode(flightInfo[0][8]), file=sys.stderr)

			session['flightInfo_flightNumber'] = flightInfo_flightNumber
			session['numberTravelers'] = numberTravelers
			session['flightTotalPrice'] = flightTotalPrice
			session['flightDepart'] = flightDepart
			session['flightDestin'] = flightDestin
			session['dt'] = DateTimeEncoder().encode(dt)
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
			print(reservationNumber + 1, file=sys.stderr)
			Time = datetime.datetime.now()
			print(str(Time), file=sys.stderr)
			Passengers = request.form['passengersName']
			print(type(Passengers), file=sys.stderr)
			Depart = session.get('flightDepart', None)
			Destin = session.get('flightDestin', None)
			Legs = Depart[selectFlight] + "_to_" + Destin[selectFlight]
			BookFee = session.get('flightTotalPrice', None)[selectFlight]

			print("CCCC",file=sys.stderr)

			ts = time.time()
			print("RRRR",file=sys.stderr)
			timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

			print(type(reservationNumber), file=sys.stderr)
			print(type(timestamp), file=sys.stderr)
			print(type(Passengers), file=sys.stderr)
			print(type(Legs), file=sys.stderr)
			print(type(BookFee), file=sys.stderr)

			print(reservationNumber + 1, file=sys.stderr)
			print(timestamp, file=sys.stderr)
			print(Passengers, file=sys.stderr)
			print(Legs, file=sys.stderr)
			print(BookFee, file=sys.stderr)

			s =  '''INSERT into Reservation (ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative) values (%d, %s, %s, %s, %s, %d, %s)''', (reservationNumber + 1, timestamp, Passengers, Legs, "21Kg bag", BookFee, Passengers)
			print("CCCCCXXXXX", file=sys.stderr)
			#print(s, file=sys.stderr)
			#cursor.execute('''INSERT into Reservation (ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative) values (%d, %s, %s, %s, %s, %d, %s)''', (111, "timestamp", "Passengers", "Legs", "21Kg bag", 222, "Passengers")) 
				#values (%d, %s, %s, %s, %s, %d, %s)''', 
				#values (66, "A", "A","A", "A", 11, "A")''')
				#(reservationNumber + 1, timestamp, Passengers, Legs, "21Kg bag", BookFee, Passengers))
				#(100, "1", "A", "A", "21Kg bag", 100, "A"))
			#sql = '''INSERT into Reservation (ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative) values (%d, '%s', '%s', '%s', '%s', %d, '%s')''' % (reservationNumber + 1, timestamp, Passengers, Legs, "21Kg bag", BookFee, Passengers)
			insertReservationSQL = "insert into Reservation values(%d, now(), '%s', '%s', '%s', %d, '%s')" %(reservationNumber + 1, Passengers, Legs, '21Kg bag', BookFee, Passengers)
			cursor.execute(insertReservationSQL)
			#cur.execute('''INSERT into Reservation (ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative)
            #      values (%s, %s, %s, %s, %s, %s, %s)''',
            #      ("11", timestamp, Passengers, Legs, "21Kg bag", Passengers))
#(ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative)
			print("AXAXAX", file=sys.stderr)
			print(type(session.get('AccountNumber')), file=sys.stderr)
			# insert Makes
			insertMakeSQL = "insert into Makes values(%d, %d)" % (session.get('AccountNumber', None) , reservationNumber + 1)
			cursor.execute(insertMakeSQL)
			print("BDDC", file=sys.stderr)


			# insert Remain
			remains = {}
			remains["flight_number"] = totalFlight[selectFlight]
			#remains["flight_number"] = session.get('flightInfo_flightNumber', None)
			remains["Date"] = session.get('dt') # acquire date by slicing datetime
			#updateSeatNumber = 
			print(remains["flight_number"])
			print(remains["Date"][1:11])

			sql = '''UPDATE  Remain 
			        SET SoldSeat = SoldSeat + %s
			        WHERE FlightNumber = %s AND
			               Date = %s '''
			print(sql, file=sys.stderr)
			print(str(session.get('numberTravelers')))
			cursor.execute(sql, (str(session.get('numberTravelers')), remains["flight_number"], remains["Date"][1:11]))
			print("success")

			# 查db當前有幾筆資料已獲得下一筆訂單編號
			#cursor2 = db.cursor()
			#curson2.execute('''INSERT into Schedule (FlightNumber, ReservationNumber)
            #      values (%s, %d)''',
            #      ("totalFlight[selectFlight]", 1))

			# 提交到数据库执行
			db.commit()

			# 把使用者選的編號的航班，訂票人數寫入Reservation
			return render_template('/dashboardUser.html')
		except:
			return 'Book Fail! Please try again.'

	# if not POST, then it is GET
	return render_template('bookFlight.html')



@app.route('/person_info', methods = ['POST','GET'])
def person_info():
	db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
	if request.method == 'POST':
		cur = db.cursor()
		cur.execute('''SELECT * FROM Customer''')
		AccountNumber = cur.rowcount
		print(AccountNumber)

		for item in request.form:
			print(item + request.form[item])

		print(datetime.datetime.now())
		try:
			sql = "INSERT INTO Customer() Values(%d, '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', now(), '%s', '%s')" \
				  %(AccountNumber+1,
					request.form['LastName'],
					request.form['FirstName'],
					request.form['Address'],
					request.form['City'],
					request.form['State'],
					request.form['Zipcode'],
					request.form['Telephone'],
					request.form['Email'],
					request.form['CreditNumber'],
					request.form['Preference'])
			print(sql)
			cur.execute(sql)
			print("INSERTION success!")
			db.commit()
			return render_template('index.html')
		except:
			return 'Customer Information Update Fail! Please try again.'
	return render_template('person_info.html')


@app.route('/login', methods=['POST'])
def login():

	db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
	cursor = db.cursor()

	#sql = "select * from account where user="+request.form['username']+" AND password="+request.form['pass']+""
    
	try:
		cursor.execute('''SELECT * from Account where UserName = %s AND Password = %s''', (request.form['username'], request.form['pass']))
		results = cursor.fetchall()
		
		if len(results) == 1:
			session['username'] = request.form['username']
			session['AccountNumber'] = results[0][0]
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
   db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
   if request.method == 'POST':
      cur = db.cursor()
      #sql = "INSERT INTO account(user, password) VALUES (" + request.form['username'] + "," + request.form['pass'] + ")"
      #sql = "INSERT INTO account(user, password) VALUES ("+request.args.get('user')+", "+request.args.get('password')+")"

      #sql = "INSERT INTO account(user, password) VALUES ("+request.form['username']+", "+request.form['password']+")"
      try:
           # 执行sql语句
         #cur.execute(sql)
         #hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
         cur.execute('''SELECT * FROM Account''')
         totalNumber = cur.rowcount
         sql_Account = "insert into Account values(%d, '%s', '%s', 0)"%(totalNumber + 1, request.form['username'], request.form['pass'])
         cur.execute(sql_Account)
         # 提交到数据库执行
         sql_Customer = "insert into Customer values(%d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', now(), '%s', '%s')"%(totalNumber + 1, 'A', 'A', 'A', 'A', 'A', '00000', 'A', 'A', 'A', 'A')
         cur.execute(sql_Customer)
         print('Success')
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