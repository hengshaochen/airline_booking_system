from flask import Flask, render_template, url_for, request, session, redirect, flash
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
			discount_ratio = cal_discount(datetime.date(year,month, day),datetime.date.today())
			# Monday = 0 , Sunday = 6
			weekday = datetime.date(year, month, day).weekday()
			weekdayLikeSearch = "%" + str(weekday) + "%"

			# check if there have enough seat
			#request.form['numberTravelers'] +
			numberTravelers = request.form['numberTravelers']
			cursor.execute('''SELECT flightNumber from Remain where numberOfSeat - soldSeat >= %s AND Date = %s''', (request.form['numberTravelers'], dt))
			availableFlight = cursor.fetchall()
			print("CDDCDCCDDCCDD")
			print(availableFlight)

			#print(availableFlight, file=sys.stderr)
			#cursor.execute('''SELECT flightNumber from Remain where  ''')
			if len(availableFlight) >= 1:
				cursor.execute('''SELECT * from Flight where origin = %s AND destination = %s AND WorkingDay LIKE %s AND flightNumber IN %s''', (request.form['from'], request.form['to'], weekdayLikeSearch, availableFlight))
				flightInfo = cursor.fetchall()
				if len(flightInfo) == 0:
					flightInfo = transferFlight(request.form['from'], request.form['to'])
					print(flightInfo)

			else:
				#cursor.execute('''SELECT flightNumber from Remain where numberOfSeat - soldSeat >= %s AND FlightNumber = %s''', (request.form['numberTravelers'], ))
				#fullOrContains = cursor.fetchall()
				#print("ALIB")
				#print(len(fullOrContains))
				#if len(fullOrContains) == 0:					
				#	sql = "insert into Remain values('%s', '%s', %d, %d);"%(flightInfo[i][0], dt, 0, flightInfo[i][1])
				#	cur.execute(sql)
				#	db.commit()
				flightInfo = []
			
			ticketDate = datetime.date(year, month, day)
			print(len(flightInfo))
			print("~~~")
			if len(flightInfo) < 1:
				print("@@@@@")
				# 模糊查詢
				print( vagueSearch('JFK', 'TPE', datetime.date(2019, 1, 1), 1) )
				print("VAGUEVAGUE")

				flightInfo, ticketDate = vagueSearch(request.form['from'], request.form['to'], datetime.date(year, month, day), 1)
				print(flightInfo)


			# 通用執行
			flightInfo_list = []
			for x in range(len(flightInfo)):
				flightInfo_list.append(list(flightInfo[x]))

			for x in range(0, len(flightInfo_list)):
				flightInfo_list[x].append(isDomesticTrip(flightInfo[x][6], flightInfo[x][7]))

			flightTotalPrice = []
			flightInfo_flightNumber = []
			flightDepart = []
			flightDestin = []
			isDomestic = []

			print("ZZZZ")

			for x in range(0, len(flightInfo)):
				flightTotalPrice.append(flightInfo[x][5] * int(numberTravelers) * discount_ratio)
				flightInfo_flightNumber.append(flightInfo[x][0])
				flightDepart.append(flightInfo[x][6])
				flightDestin.append(flightInfo[x][7])
				isDomestic.append(isDomesticTrip(flightInfo[x][6], flightInfo[x][7]))

			session['flightInfo_flightNumber'] = flightInfo_flightNumber
			session['numberTravelers'] = numberTravelers
			session['flightTotalPrice'] = flightTotalPrice
			session['flightDepart'] = flightDepart
			session['flightDestin'] = flightDestin
			session['dt'] = DateTimeEncoder().encode(dt)
			session['ticketDate'] = DateTimeEncoder().encode(ticketDate);
			return render_template('bookFlight.html', flightInfo=flightInfo, numberTravelers=numberTravelers, flightTotalPrice=flightTotalPrice, isDomestic=isDomestic, flightInfo_list=flightInfo_list, ticketDate=ticketDate)

		except:
			return 'Register Fail! Please try again.'

	# if not POST, then it is GET
	return render_template('dashboardUser.html')




@app.route('/dashboardUser_roundTrip', methods=['POST', 'GET'])
def dashboardUser_roundTrip():

	print('dashboardUser_roundTrip TEST!', file=sys.stderr)
	# POST
	if request.method == 'POST':
		try:
			db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
			cursor = db.cursor()

			# Get the weekday of the depart time
			dt = request.form['depeartDate']
			dt_return = request.form['returnDate']
			print(dt)
			print("VVVVV")
			print(dt_return)
			year, month, day = (int(x) for x in dt.split('-'))
			year_r, month_r, day_r = (int(x) for x in dt_return.split('-'))
			discount_ratio = cal_discount(datetime.date(year,month, day),datetime.date.today())
			# Monday = 0 , Sunday = 6
			weekday = datetime.date(year, month, day).weekday()
			weekdayLikeSearch = "%" + str(weekday) + "%"

			# check if there have enough seat
			#request.form['numberTravelers'] +
			numberTravelers = request.form['numberTravelers']
			cursor.execute('''SELECT flightNumber from Remain where numberOfSeat - soldSeat >= %s AND Date = %s''', (request.form['numberTravelers'], dt))
			availableFlight = cursor.fetchall()
			cursor.execute('''SELECT flightNumber from Remain where numberOfSeat - soldSeat >= %s AND Date = %s''', (request.form['numberTravelers'], dt_return))
			availableFlight_return = cursor.fetchall()
			print("CDDCDCCDDCCDD")
			print(availableFlight)
			#print(availableFlight, file=sys.stderr)
			#cursor.execute('''SELECT flightNumber from Remain where  ''')

			if len(availableFlight) >= 1:
				cursor.execute('''SELECT * from Flight where origin = %s AND destination = %s AND WorkingDay LIKE %s AND flightNumber IN %s''', (request.form['from'], request.form['to'], weekdayLikeSearch, availableFlight))
				flightInfo = cursor.fetchall()
			else:
				flightInfo = []

			ticketDate = datetime.date(year, month, day)

			if len(availableFlight_return) >= 1:
				cursor.execute('''SELECT * from Flight where origin = %s AND destination = %s AND WorkingDay LIKE %s AND flightNumber IN %s''', (request.form['to'], request.form['from'], weekdayLikeSearch, availableFlight_return))
				flightInfo_return = cursor.fetchall()
			else:
				flightInfo_return = []
			
			ticketDate_return = datetime.date(year_r, month_r, day_r)

			print("~~~")
			if len(flightInfo) < 1:
				print("@@@@@")
				# 模糊查詢
				print("VAGUEVAGUE")

				flightInfo, ticketDate = vagueSearch(request.form['from'], request.form['to'], datetime.date(year, month, day), 1)
				print(flightInfo)
			if len(flightInfo_return) < 1:
				print("@@@@@")
				# 模糊查詢
				print("2vague")

				print(datetime.date(year_r, month_r, day_r))
				print(request.form['to'])
				print(request.form['from'])
				flightInfo_return, ticketDate_return = vagueSearch(request.form['to'], request.form['from'], datetime.date(year_r, month_r, day_r), 1)
				print(flightInfo_return)


			# 通用執行
			flightInfo_list = []
			flightInfo_list_return = []
			for x in range(len(flightInfo)):
				flightInfo_list.append(list(flightInfo[x]))

			for x in range(len(flightInfo_return)):
				flightInfo_list_return.append(list(flightInfo_return[x]))

			for x in range(0, len(flightInfo_list)):
				flightInfo_list[x].append(isDomesticTrip(flightInfo[x][6], flightInfo[x][7]))

			for x in range(0, len(flightInfo_list_return)):
				flightInfo_list_return[x].append(isDomesticTrip(flightInfo_return[x][6], flightInfo_return[x][7]))

			print("IOOOO")
			flightTotalPrice = []
			flightInfo_flightNumber = []
			flightDepart = []
			flightDestin = []
			isDomestic = []
			flightTotalPrice_return = []
			flightInfo_flightNumber_return = []
			flightDepart_return = []
			flightDestin_return = []
			isDomestic_return = []

			for x in range(0, len(flightInfo)):
				flightTotalPrice.append(flightInfo[x][5] * int(numberTravelers) * discount_ratio)
				flightInfo_flightNumber.append(flightInfo[x][0])
				flightDepart.append(flightInfo[x][6])
				flightDestin.append(flightInfo[x][7])
				isDomestic.append(isDomesticTrip(flightInfo[x][6], flightInfo[x][7]))

			for x in range(0, len(flightInfo_return)):
				flightTotalPrice_return.append(flightInfo_return[x][5] * int(numberTravelers) * discount_ratio)
				flightInfo_flightNumber_return.append(flightInfo_return[x][0])
				flightDepart_return.append(flightInfo_return[x][6])
				flightDestin_return.append(flightInfo_return[x][7])
				isDomestic_return.append(isDomesticTrip(flightInfo_return[x][6], flightInfo_return[x][7]))

			print(flightTotalPrice[0])
			print(flightTotalPrice_return)
			print("dwwccwewcwe")

			session['flightInfo_flightNumber'] = flightInfo_flightNumber
			session['numberTravelers'] = numberTravelers
			session['flightTotalPrice'] = flightTotalPrice
			session['flightDepart'] = flightDepart
			session['flightDestin'] = flightDestin
			session['dt'] = DateTimeEncoder().encode(dt)
			session['round1'] = DateTimeEncoder().encode(ticketDate)
			session['round2'] = DateTimeEncoder().encode(ticketDate_return)

			session['flightInfo_flightNumber_return'] = flightInfo_flightNumber_return
			session['numberTravelers'] = numberTravelers
			session['flightTotalPrice_return'] = flightTotalPrice_return
			session['flightDepart_return'] = flightDepart_return
			session['flightDestin_return'] = flightDestin_return
			session['dt_return'] = DateTimeEncoder().encode(dt_return)

			print(flightInfo_list_return)
			print("sdscwceew")

			return render_template('bookFlight_roundtrip.html', flightInfo=flightInfo, 
				flightInfo_return=flightInfo_return, numberTravelers=numberTravelers, 
				flightTotalPrice=flightTotalPrice, flightTotalPrice_return=flightTotalPrice_return, isDomestic=isDomestic, 
				flightInfo_list=flightInfo_list, flightInfo_list_return=flightInfo_list_return, 
				ticketDate=ticketDate, ticketDate_return=ticketDate_return)

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
			#remains["Date"] = session.get('dt') # acquire date by slicing datetime
			remains["Date"] = session.get('ticketDate')
			#updateSeatNumber = 
			print(remains["flight_number"])
			print(remains["Date"][1:11])
			print(session.get('ticketDate'))
			print("OOPPPPP")

			sql = '''UPDATE  Remain 
			        SET SoldSeat = SoldSeat + %s
			        WHERE FlightNumber = %s AND
			               Date = %s '''
			print(sql, file=sys.stderr)
			print(str(session.get('numberTravelers')))
			cursor.execute(sql, (str(session.get('numberTravelers')), remains["flight_number"], remains["Date"][1:11]))
			print("success")

			# 查db當前有幾筆資料已獲得下一筆訂單編號
			cursor2 = db.cursor()

			Schedule_insert = "insert into Schedule values('%s', %d, '%s')" % ( totalFlight[selectFlight], reservationNumber + 1, remains["Date"][1:11] )

			cursor2.execute(Schedule_insert)
			#curson2.execute('''INSERT into Schedule (FlightNumber, ReservationNumber, FlightDate)
            #      values ('%s', %d, %s)''',
            #      ("totalFlight[selectFlight]", 1, remains["Date"]))

			print("XXXX")
			# 提交到数据库执行
			db.commit()

			# 把使用者選的編號的航班，訂票人數寫入Reservation
			flash('You were successfully book the one way ticket!')
			return render_template('/dashboardUser.html')
		except:
			return 'Book Fail! Please try again.'

	# if not POST, then it is GET
	return render_template('bookFlight.html')



@app.route('/bookFlight_roundtrip', methods=['POST', 'GET'])
def bookFlight_roundtrip():

	print('bookFlight_roundtrip Test!', file=sys.stderr)
	# POST
	if request.method == 'POST':
		try:
			db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
			#cursor = db.cursor()

			totalFlight = session.get('flightInfo_flightNumber', None)
			totalFlight_return = session.get('flightInfo_flightNumber_return', None)
			selectFlight = int(request.form['selectFlight']) - 1
			selectFlight_return = int(request.form['selectFlightReturn']) - 1

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

			Legs_return = Destin[selectFlight] + "_to_" + Depart[selectFlight]
			BookFee_return = session.get('flightTotalPrice_return', None)[selectFlight_return]

			print("CCCC",file=sys.stderr)
			print(BookFee_return)
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
			s =  '''INSERT into Reservation (ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative) values (%d, %s, %s, %s, %s, %d, %s)''', (reservationNumber + 2, timestamp, Passengers, Legs_return, "21Kg bag", BookFee_return, Passengers)
			print("CCCCCXXXXX", file=sys.stderr)
			#print(s, file=sys.stderr)
			#cursor.execute('''INSERT into Reservation (ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative) values (%d, %s, %s, %s, %s, %d, %s)''', (111, "timestamp", "Passengers", "Legs", "21Kg bag", 222, "Passengers")) 
				#values (%d, %s, %s, %s, %s, %d, %s)''', 
				#values (66, "A", "A","A", "A", 11, "A")''')
				#(reservationNumber + 1, timestamp, Passengers, Legs, "21Kg bag", BookFee, Passengers))
				#(100, "1", "A", "A", "21Kg bag", 100, "A"))
			#sql = '''INSERT into Reservation (ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative) values (%d, '%s', '%s', '%s', '%s', %d, '%s')''' % (reservationNumber + 1, timestamp, Passengers, Legs, "21Kg bag", BookFee, Passengers)
			insertReservationSQL = "insert into Reservation values(%d, now(), '%s', '%s', '%s', %d, '%s')" %(reservationNumber + 1, Passengers, Legs, '21Kg bag', BookFee, Passengers)
			insertReservationSQL_return = "insert into Reservation values(%d, now(), '%s', '%s', '%s', %d, '%s')" %(reservationNumber + 2, Passengers, Legs_return, '21Kg bag', BookFee_return, Passengers)
			cursor.execute(insertReservationSQL)
			cursor.execute(insertReservationSQL_return)
			#cur.execute('''INSERT into Reservation (ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative)
            #      values (%s, %s, %s, %s, %s, %s, %s)''',
            #      ("11", timestamp, Passengers, Legs, "21Kg bag", Passengers))
#(ReservationNumber, Time, Passengers, Legs, FareRestrictions, BookFee, CustomerRepresentative)
			print("AXAXAX", file=sys.stderr)
			print(type(session.get('AccountNumber')), file=sys.stderr)
			# insert Makes
			insertMakeSQL = "insert into Makes values(%d, %d)" % (session.get('AccountNumber', None) , reservationNumber + 1)
			insertMakeSQL_return = "insert into Makes values(%d, %d)" % (session.get('AccountNumber', None) , reservationNumber + 2)
			cursor.execute(insertMakeSQL)
			cursor.execute(insertMakeSQL_return)
			print("BDDC", file=sys.stderr)


			# insert Remain
			remains = {}
			remains["flight_number"] = totalFlight[selectFlight]
			remains_return = {}
			remains_return["flight_number"] = totalFlight_return[selectFlight_return]
			#remains["flight_number"] = session.get('flightInfo_flightNumber', None)
			#remains["Date"] = session.get('dt') # acquire date by slicing datetime

			remains["Date"] = session.get('round1')
			remains_return["Date"] = session.get('round2') # acquire date by slicing datetime
			#updateSeatNumber = 
			print(remains["flight_number"])
			print("@@@")
			#print(remains["Date"][1:11])
			print(remains["Date"])
			sql = '''UPDATE  Remain 
			        SET SoldSeat = SoldSeat + %s
			        WHERE FlightNumber = %s AND
			               Date = %s '''
			print(sql, file=sys.stderr)
			print(str(session.get('numberTravelers')))
			cursor.execute(sql, (str(session.get('numberTravelers')), remains["flight_number"], remains["Date"][1:11]))
			cursor.execute(sql, (str(session.get('numberTravelers')), remains_return["flight_number"], remains_return["Date"][1:11]))
			print(remains['Date'])
			print(remains_return['Date'])
			print("success")

			# 查db當前有幾筆資料已獲得下一筆訂單編號
			cursor2 = db.cursor()

			Schedule_insert = "insert into Schedule values('%s', %d, '%s')" % ( totalFlight[selectFlight], reservationNumber + 1, remains["Date"][1:11] )
			Schedule_insert_return = "insert into Schedule values('%s', %d, '%s')" % ( totalFlight_return[selectFlight_return], reservationNumber + 2, remains_return["Date"][1:11] )

			cursor2.execute(Schedule_insert)
			cursor2.execute(Schedule_insert_return)
			#curson2.execute('''INSERT into Schedule (FlightNumber, ReservationNumber, FlightDate)
            #      values ('%s', %d, %s)''',
            #      ("totalFlight[selectFlight]", 1, remains["Date"]))

			print("XXXX")
			# 提交到数据库执行
			db.commit()

			# 把使用者選的編號的航班，訂票人數寫入Reservation
			flash('You were successfully book the round trip ticket!')
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
		AccountNumber = session.get('AccountNumber')
		print(AccountNumber)

		for item in request.form:
			print(item + request.form[item])

		print(datetime.datetime.now())
		try:



			sql = "UPDATE  Customer SET LastName = '%s', FirstName = '%s', Address = '%s', " \
				  "City = '%s', State = '%s', ZipCode = '%s' ,Telephone = '%s', Email = '%s', AccountCreationTime = now(), " \
				  "CreditCardNumber = '%s', Preferences = '%s' WHERE AccountNumber = '%s'" %(request.form['LastName'], request.form['FirstName'],
																					   request.form['Address'], request.form['City'],
																					   request.form['State'],
																					   request.form['Zipcode'], request.form['Telephone'],
																					   request.form['Email'], request.form['CreditNumber'],
																					   request.form['Preference'], session.get('AccountNumber') )

			#sql = '''UPDATE  Customer SET LastName = %s, FirstName = %s, Address = %s, City = %s, State = %s, ZipCode = %s, Telephone = %s, Email = %s, AccountCreationTime = now(), CreditCardNumber = %s, Preferences = %s WHERE AccountNumber = %s''' %(request.form['LastName'], request.form['FirstName'], request.form['LastName'], request.form['Address'], request.form['City'], request.form['State'], request.form['Zipcode'], request.form['Telephone'], request.form['Email'], request.form['CreditNumber'], request.form['Preference'], session.get('AccountNumber')	)

			print(sql)
			print("DDDD")
			#cur.execute(sql, (request.form['LastName'], request.form['FirstName'], request.form['Address'], request.form['City'], request.form['State'], request.form['Zipcode'], request.form['Telephone'], request.form['Email'], request.form['CreditNumber'], request.form['Preference'], session.get('AccountNumber') ))
			cur.execute(sql)
			print("INSERTION success!")
			db.commit()
			flash('You were successfully modify the personal information')
			return render_template('dashboardUser.html')
		except:
			return 'Customer Information Update Fail! Please try again.'
	return render_template('person_info.html')


@app.route('/reservation_history', methods = ['POST','GET'])
def reservation_history():
	db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
	if request.method == 'POST':
		cur = db.cursor()
		sql_1 = "select ReservationNumber from Makes where AccountNumber=%d"%(session.get('AccountNumber'))
		# cur.execute('''SELECT ReservationNumber FROM Makes WHERE AccountNumber = %s''', (session.get('AccountNumber')))
		# makesSQL = ('''SELECT ReservationNumber FROM Makes WHERE AccountNumber = %s''', (session.get('AccountNumber')))
		#MakesSQL = cur.fetchall()
		cur.execute(sql_1)
		aa = cur.fetchall();
		print(aa)
		sql_2 = "select * from Reservation where ReservationNumber in (%s)"%(sql_1)
		#sql_2_result = cur.fetchall()
		#sql_3 = "select * from (%s) where ReservationNumber = (%s)" % (sql_2_result,)
		# cur.execute('''SELECT * FROM Reservation WHERE ReservationNumber IN (%s)''', sql_1)
		cur.execute(sql_2)
		reservationQuery = cur.fetchall()
		print(reservationQuery)
		print("Test")

		try:

			return render_template('reservation_history.html', reservationQuery=reservationQuery)
		except:
			return 'Query Fail! Please try again.'
	return render_template('person_info.html')


@app.route('/reservation_history_just_one', methods = ['POST','GET'])
def reservation_history_just_one():
	db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
	if request.method == 'POST':
		cur = db.cursor()
		sql_1 = "select ReservationNumber from Makes where AccountNumber=%d"%(session.get('AccountNumber'))
		# cur.execute('''SELECT ReservationNumber FROM Makes WHERE AccountNumber = %s''', (session.get('AccountNumber')))
		# makesSQL = ('''SELECT ReservationNumber FROM Makes WHERE AccountNumber = %s''', (session.get('AccountNumber')))
		#MakesSQL = cur.fetchall()
		cur.execute(sql_1)

		#session['queryReservationNumber'] = request.form['queryReservationNumber']
		aa = cur.fetchall();
		print("OOOOOOOOOOO")
		print(request.form['queryReservationNumber'])
		sql_2 = "select * from Reservation where ReservationNumber in (%s) and ReservationNumber = %d"%(sql_1, int(request.form['queryReservationNumber']))
		cur.execute(sql_2)
		one_result = cur.fetchall()
		print("XXXXSXSXS")
		print(one_result)
		#sql_3 = "select * from (%s) where ReservationNumber = (%s)" % (sql_2_result,)
		# cur.execute('''SELECT * FROM Reservation WHERE ReservationNumber IN (%s)''', sql_1)
		#cur.execute(sql_2)
		#reservationQuery = cur.fetchall()
		#print(reservationQuery)
		print("Test")

		try:

			return render_template('reservation_history_just_one.html', one_result=one_result)
		except:
			return 'Query Fail! Please try again.'
	return render_template('person_info.html')


@app.route('/order_query_past',methods = ['POST', 'GET'])
def order_query_past():
	if request.method == 'POST':
		AccountNumber = session.get('AccountNumber')
		order_history_table = reservation_timestamp_past(AccountNumber, False)
		try:
			return render_template('order_history.html',order_history_table = order_history_table)
		except:
			return "Query history failed, please try again."
	return render_template('person_info.html')

@app.route('/order_query_future',methods = ['POST', 'GET'])
def order_query_future():
	if request.method == 'POST':
		AccountNumber = session.get('AccountNumber')
		order_history_table = reservation_timestamp_past(AccountNumber, True)
		try:
			return render_template('order_history.html',order_history_table = order_history_table)
		except:
			return "Query history failed, please try again."
	return render_template('person_info.html')


@app.route('/find_best', methods = ['POST','GET'])
def find_best():
	if request.method == 'POST':
		date = request.form['best_date']
		print(type(date))
		table = findBestSeller(date)
		try:
			return render_template('find_best_seller.html',bestSeller = table)
		except:
			return "Find best seller failed, please try again!"
	return render_template('person_info.html')


@app.route('/find_least', methods = ['POST','GET'])
def find_least():
	if request.method == 'POST':
		date = request.form['least_date']
		print(type(date))
		table = findLeastSeller(date)
		try:
			print(table)
			return render_template('find_least_seller.html',leastSeller = table)
		except:
			return "Find least seller failed, please try again!"
	return render_template('person_info.html')


@app.route('/modifyPassword', methods = ['POST'])
def modifyPassword():

	db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
	cursor = db.cursor()
	if request.method == 'POST':
		try:

			sql = '''UPDATE  Account 
			        SET Password = %s
			        WHERE UserName = %s'''
			print(sql)
			cursor.execute(sql, (request.form['newPassword'], session.get('username')))
			db.commit()
			flash('You were successfully modify the password')
			return render_template('dashboardUser.html')
		except:
			return "Password modify failed, please try again!"
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
			if results[0][3] == 1:
				# admin
				return render_template('dashboardAdmin.html')
			else:
				# user
				return render_template('dashboardUser.html')
			#print(results[0][2], file=sys.stderr)

			#return render_template('dashboard.html', your_list=results[0][2])

		else:
			return 'Login Fail, please double check your username or password'
	except:
		return 'Fail'

    #if login_user:
    #	# 如果user存在，驗證db中的password是否跟使用者輸入的相同
    #    if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
    #        session['username'] = request.form['username']
    #        return redirect(url_for('index'))

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
         print(totalNumber)
         sql_Account = "insert into Account values(%d, '%s', '%s', 0)"%(totalNumber + 1, request.form['username'], request.form['pass'])
         cur.execute(sql_Account)
         print("CDCCDCD")

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


def isDomesticTrip(__from__, __to__):
    """
    use to know whether a flight is domestic or not
    :param __from__: string
    :param __to__: string
    :return: boolean
    """
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cur = db.cursor()
    sql_from = "select Country from Airport where AirportID='%s'"%(__from__)
    cur.execute(sql_from)
    country_from = cur.fetchall()
    sql_to = "select Country from Airport where AirportID='%s'"%(__to__)
    cur.execute(sql_to)
    country_to = cur.fetchall()

    if country_from == country_to:
        return "Domestic"
    return "International"

def vagueSearch(__from__, __to__, __date__, __number__):
    """
    when the specific day is all sold out, use this to vague search
    :param __from__: string
    :param __to__: string
    :param __date__: string '2018-03-31'
    :param __number__: int
    :return: result set
    """

    # define time duration
    oneday = datetime.timedelta(days=1)
    __date__ += oneday
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cur = db.cursor()
    while True:
        # Monday = 0 , Sunday = 6
        weekday = __date__.weekday()
        weekdayLikeSearch = "%" + str(weekday) + "%"

        sql = "select FlightNumber, NumberOfSeat from Flight where origin='%s' and destination='%s' and WorkingDay like '%s'"%(__from__, __to__, weekdayLikeSearch)
        sql_result = "select * from Flight where origin='%s' and destination='%s' and WorkingDay like '%s'"%(__from__, __to__, weekdayLikeSearch)

        cur.execute(sql)
        flightInfo = cur.fetchall()

        cur.execute(sql_result)
        flightResult = cur.fetchall()
        print(flightInfo)
        if 0 == len(flightInfo):
            __date__ = __date__ + oneday
            continue

        for i in range(len(flightInfo)):
            sql = "select * from Remain where FlightNumber='%s' and Date='%s';"%(flightInfo[i][0], __date__)
            cur.execute(sql)
            res = cur.fetchall()

            if 0 == len(res):
                sql = "insert into Remain values('%s', '%s', %d, %d);"%(flightInfo[i][0], __date__, 0, flightInfo[i][1])
                cur.execute(sql)
                db.commit()

        return flightResult, __date__



def reservation_timestamp_past(account, past_future):
    """
    when the specific day is all sold out, use this to vague search
    :param __date__: string '2018-03-31' or '2018-03-31 11:11:11'
    :param _account_: int
    :return: result set
    """
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cur = db.cursor()
    # _start_ += " 00:00:00"
    # _end_ += "23:59:59"

    reserv_in_make_sql = "SELECT ReservationNumber FROM Makes WHERE AccountNumber=%d" % account
    print("select in Make")
    print(reserv_in_make_sql)
    cur.execute(reserv_in_make_sql)
    reserv_num = cur.fetchall()
    print(reserv_num)

    if past_future == True:
    	# Future
    	reserve_in_reserv_sql = "SELECT ReservationNumber FROM Schedule " \
          	"WHERE ReservationNumber IN (%s) AND " \
          	"timediff(now(), timestamp(FlightDate)) < 0 " % reserv_in_make_sql
    else:
    	# Past
    	reserve_in_reserv_sql = "SELECT ReservationNumber FROM Schedule " \
          	"WHERE ReservationNumber IN (%s) AND " \
          	"timediff(now(), timestamp(FlightDate)) > 0 " % reserv_in_make_sql

    print("select in ReservationNumber")
    print(reserve_in_reserv_sql)
    cur.execute(reserve_in_reserv_sql)
    print(cur.fetchall())
    #reserv_num = cur.fetchall()


    sql = "SELECT * FROM Reservation WHERE ReservationNumber IN (%s)" % reserve_in_reserv_sql
    print("select in Reservation table")
    print(sql)
    cur.execute(sql)
    reserv_past = cur.fetchall()
    return reserv_past


def findBestSeller(__date__):
    """
    this fuction is used find the best sold flight on the date chosen by user
    :param __date__: datetime.date()
    :return: flight info
    """

    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cur = db.cursor()
    #sql = "select f.FlightNumber, f.origin, f.destination, max(SoldSeat) from Flight f join Remain r using(FlightNumber) where r.Date='%s';"%(__date__)
    sql = "select FlightNumber, origin , destination, max(SoldSeat) from Remain join Flight using(FlightNumber) where Date='%s' and SoldSeat = (select max(SoldSeat) from Remain where Date='%s');" %(__date__,__date__)
    cur.execute(sql)
    return cur.fetchall()


def findLeastSeller(__date__):
    """
    this fuction is used find the best sold flight on the date chosen by user
    :param __date__: datetime.date()
    :return: flight info
    """

    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cur = db.cursor()
    sql = "select f.FlightNumber, f.origin, f.destination, min(SoldSeat) from Flight f join Remain r using(FlightNumber) where r.Date='%s';"%(__date__)
    cur.execute(sql)
    return cur.fetchall()



@app.route('/dashboardAdmin', methods=['POST', 'GET'])
def dashboardAdmin():
    # db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    # cursor = db.cursor()
    if request.method == 'POST':
        return render_template('dashboardAdmin1.html')
        return render_template('dashboardAdmin2.html')
        return render_template('dashboardAdmin3.html')
        return render_template('dashboardAdmin4.html')
        return render_template('dashboardAdmin5.html')
        return render_template('dashboardAdmin6.html')
        return render_template('dashboardAdmin7.html')
        return render_template('dashboardAdmin8.html')
        return render_template('dashboardAdmin9.html')
        return render_template('dashboardAdmin10.html')
        # request.form["b1"]



@app.route('/dashboardAdmin1', methods=['POST', 'GET'])
def dashboardAdmin1():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )


    if request.method == 'POST':

        return render_template('dashboardAdmin1.html')
        cursor = db.cursor()
        try:
            key=[request.form['cust_name1'],request.form['accountnum1'],request.form['lastname1'],request.form['firstname1'],request.form['address1'],request.form['city1'],request.form['phone1']]
            if key[0] != "":
                cust_name1 = key[0]
                cursor.execute('''SELECT * from Customer WHERE FirstName = %s and LastName = %s''',(cust_name1.split(" ")[0],cust_name1.split(" ")[1]))
                cust_info = cursor.fetchall()
            if key[0] == "":
                cursor.execute("update Customer set Lastname = %s where AccountNumber = %s",(request.form['lastname1'],request.form['accountnum1']))
                cursor.execute("update Customer set Firstname = %s where AccountNumber = %s",
                               (request.form['firstname1'], request.form['accountnum1']))
                cursor.execute("update Customer set Address = %s where AccountNumber = %s",
                               (request.form['address1'], request.form['accountnum1']))
                cursor.execute("update Customer set City = %s where AccountNumber = %s",
                               (request.form['city1'], request.form['accountnum1']))
                cursor.execute("update Customer set Telephone = %s where AccountNumber = %s",
                               (request.form['phone1'], request.form['accountnum1']))
                cursor.execute('''SELECT * from Customer 
                WHERE AccountNumber = %s''',(request.form['accountnum1']))
                cust_info = cursor.fetchall()

        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin1.html', cust_info = cust_info)


@app.route('/d1', methods=['POST', 'GET'])
def d1():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )


    if request.method == 'POST':
        cursor = db.cursor()
        try:
            key=[request.form['cust_name1'],request.form['accountnum1'],request.form['lastname1'],request.form['firstname1'],request.form['address1'],request.form['city1'],request.form['phone1']]
            if key[0] != "":
                cust_name1 = key[0]
                cursor.execute('''SELECT * from Customer WHERE FirstName = %s and LastName = %s''',(cust_name1.split(" ")[0],cust_name1.split(" ")[1]))
                cust_info = cursor.fetchall()
            if key[0] == "":
                cursor.execute("update Customer set Lastname = %s where AccountNumber = %s",(request.form['lastname1'],request.form['accountnum1']))
                cursor.execute("update Customer set Firstname = %s where AccountNumber = %s",
                               (request.form['firstname1'], request.form['accountnum1']))
                cursor.execute("update Customer set Address = %s where AccountNumber = %s",
                               (request.form['address1'], request.form['accountnum1']))
                cursor.execute("update Customer set City = %s where AccountNumber = %s",
                               (request.form['city1'], request.form['accountnum1']))
                cursor.execute("update Customer set Telephone = %s where AccountNumber = %s",
                               (request.form['phone1'], request.form['accountnum1']))
                cursor.execute('''SELECT * from Customer 
                WHERE AccountNumber = %s''',(request.form['accountnum1']))
                cust_info = cursor.fetchall()

        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin1.html', cust_info = cust_info)


@app.route('/dashboardAdmin2', methods=['POST', 'GET'])
def dashboardAdmin2():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()
    if request.method == 'POST':
        return render_template('dashboardAdmin2.html')
        try:
            time = request.form['time1']

            month = time.split("-")[0]
            year = time.split("-")[1]

            cursor.execute('''SELECT *
                    from Reservation r
                    where month(r.Time) = %s and year(r.Time) = %s ''',(month,year))
            sales = cursor.fetchall()
            print(sales)

        except:
            return 'Register Fail! Please try again.'
    return render_template('dashboardAdmin2.html', sales = sales)


@app.route('/d2', methods=['POST', 'GET'])
def d2():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()
    if request.method == 'POST':
        try:
            time = request.form['time1']

            month = time.split("-")[0]
            year = time.split("-")[1]

            cursor.execute('''SELECT *
                    from Reservation r
                    where month(r.Time) = %s and year(r.Time) = %s ''',(month,year))
            sales = cursor.fetchall()
            print(sales)

        except:
            return 'Register Fail! Please try again.'
    return render_template('dashboardAdmin2.html', sales = sales)


@app.route('/dashboardAdmin3', methods=['POST', 'GET'])
def dashboardAdmin3():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cursor = db.cursor()

    if request.method == 'POST':
        return render_template('dashboardAdmin3.html')
        try:
            cursor.execute('''SELECT * from Flight''')
            flights_list = cursor.fetchall()
            print(flights_list)
        except:
            return 'Register Fail! Please try again.'

    return render_template('dashboardAdmin3.html', flights_list=flights_list)

@app.route('/d3', methods=['POST', 'GET'])
def d3():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            cursor.execute('''SELECT * from Flight''')
            flights_list = cursor.fetchall()
            print(flights_list)
        except:
            return 'Register Fail! Please try again.'

    return render_template('dashboardAdmin3.html', flights_list=flights_list)


@app.route('/dashboardAdmin4', methods=['POST', 'GET'])
def dashboardAdmin4():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()
    if request.method == 'POST':
        return render_template('dashboardAdmin4.html')
        try:

            key1 = [request.form['flight_num2'],request.form['cust_name3']]
            if key1[0]!= " " and key1[1] == "":
                flight_num = key1[0]
                cursor.execute('''select *
                                    from SearchResv
                                    where FlightNumber=%s ''', flight_num)
                res_num = cursor.fetchall()
                # print(res_num)

            elif key1[1]!= " " and key1[0] == "":
                cust_name = key1[1]
                print(cust_name.split(" ")[0])
                cursor.execute('''select *
                                from SearchResv
                                where FirstName=%s and LastName=%s ''',(cust_name.split(" ")[0],cust_name.split(" ")[1]))

                res_num = cursor.fetchall()
                # print(res_num)
            # elif key1[1]!= "" and key1[0] == "":
            #     res_num =

        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin4.html',res_num=res_num)



@app.route('/d4', methods=['POST', 'GET'])
def d4():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()
    if request.method == 'POST':
        try:

            key1 = [request.form['flight_num2'],request.form['cust_name3']]
            if key1[0]!= " " and key1[1] == "":
                flight_num = key1[0]
                cursor.execute('''select *
                                    from SearchResv
                                    where FlightNumber=%s ''', flight_num)
                res_num = cursor.fetchall()
                # print(res_num)

            elif key1[1]!= " " and key1[0] == "":
                cust_name = key1[1]
                print(cust_name.split(" ")[0])
                cursor.execute('''select *
                                from SearchResv
                                where FirstName=%s and LastName=%s ''',(cust_name.split(" ")[0],cust_name.split(" ")[1]))

                res_num = cursor.fetchall()
                # print(res_num)
            # elif key1[1]!= "" and key1[0] == "":
            #     res_num =

        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin4.html',res_num=res_num)


@app.route('/dashboardAdmin5', methods=['POST', 'GET'])
def dashboardAdmin5():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()
    if request.method == 'POST':
        return render_template('dashboardAdmin5.html')
        try:

            key1 = [request.form['flight_num5'],request.form['city5'],request.form['cust_name5']]
            if key1[0]!= " " and key1[1] == "" and key1[2] == "":
                flight_num = key1[0]
                cursor.execute('''select sum(SoldSeat)
                                    from Remain
                                    where FlightNumber=%s ''', flight_num)
                seat_num = cursor.fetchall()
                print(int(seat_num[0][0]))
                cursor.execute('''select Fare
                                    from Flight
                                    where FlightNumber=%s ''', flight_num)
                price = cursor.fetchall()
                print(int(price[0][0]))
                revenue = int(seat_num[0][0]) * int(price[0][0])

            if key1[0] == "" and key1[1] == "" and key1[2] != "":
                cust_num = key1[2]
                print(cust_num)
                # sql = "select sum(r.BookFee) from Reservation r where r.ReservationNumber in (select ReservationNumber from Makes where AccountNumber=1)"
                cursor.execute("select sum(r.BookFee) from Reservation r where r.ReservationNumber in (select ReservationNumber from Makes where AccountNumber=%s)",cust_num)
                revenue = cursor.fetchall()[0][0]

            if key1[0] == "" and key1[1] != "" and key1[2] == "":
                city= key1[1]

                # sql = "select sum(r.BookFee) from Reservation r where r.ReservationNumber in (select ReservationNumber from Makes where AccountNumber=1)"
                cursor.execute(
                    "select sum(r.SoldSeat * f.Fare) from Remain r left join Flight f using(FlightNumber) left join Airport a on f.destination = a.AirportID where a.city = %s",city)
                revenue = cursor.fetchall()[0][0]




                # print(res_num)

            # elif key1[1]!= " " and key1[0] == "":
            #     cust_name = key1[1]
            #     print(cust_name.split(" ")[0])
            #     cursor.execute('''select *
            #                     from SearchResv
            #                     where FirstName=%s and LastName=%s ''',(cust_name.split(" ")[0],cust_name.split(" ")[1]))
            #
            #     res_num = cursor.fetchall()
                # print(res_num)
            # elif key1[1]!= "" and key1[0] == "":
            #     res_num =

        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin5.html',revenue=revenue)


@app.route('/d5', methods=['POST', 'GET'])
def d5():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()
    if request.method == 'POST':
        try:

            key1 = [request.form['flight_num5'],request.form['city5'],request.form['cust_name5']]
            if key1[0]!= " " and key1[1] == "" and key1[2] == "":
                flight_num = key1[0]
                cursor.execute('''select sum(SoldSeat)
                                    from Remain
                                    where FlightNumber=%s ''', flight_num)
                seat_num = cursor.fetchall()
                print(int(seat_num[0][0]))
                cursor.execute('''select Fare
                                    from Flight
                                    where FlightNumber=%s ''', flight_num)
                price = cursor.fetchall()
                print(int(price[0][0]))
                revenue = int(seat_num[0][0]) * int(price[0][0])

            if key1[0] == "" and key1[1] == "" and key1[2] != "":
                cust_num = key1[2]
                print(cust_num)
                # sql = "select sum(r.BookFee) from Reservation r where r.ReservationNumber in (select ReservationNumber from Makes where AccountNumber=1)"
                cursor.execute("select sum(r.BookFee) from Reservation r where r.ReservationNumber in (select ReservationNumber from Makes where AccountNumber=%s)",cust_num)
                revenue = cursor.fetchall()[0][0]

            if key1[0] == "" and key1[1] != "" and key1[2] == "":
                city= key1[1]

                # sql = "select sum(r.BookFee) from Reservation r where r.ReservationNumber in (select ReservationNumber from Makes where AccountNumber=1)"
                cursor.execute(
                    "select sum(r.SoldSeat * f.Fare) from Remain r left join Flight f using(FlightNumber) left join Airport a on f.destination = a.AirportID where a.city = %s",city)
                revenue = cursor.fetchall()[0][0]




                # print(res_num)

            # elif key1[1]!= " " and key1[0] == "":
            #     cust_name = key1[1]
            #     print(cust_name.split(" ")[0])
            #     cursor.execute('''select *
            #                     from SearchResv
            #                     where FirstName=%s and LastName=%s ''',(cust_name.split(" ")[0],cust_name.split(" ")[1]))
            #
            #     res_num = cursor.fetchall()
                # print(res_num)
            # elif key1[1]!= "" and key1[0] == "":
            #     res_num =

        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin5.html',revenue=revenue)


@app.route('/dashboardAdmin6', methods=['POST', 'GET'])
def dashboardAdmin6():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cursor = db.cursor()

    if request.method == 'POST':
        return render_template('dashboardAdmin6.html')
        try:
            cursor.execute("select m.AccountNumber, sum(r.BookFee) as total "
                           "from Makes m join Reservation r using(ReservationNumber) "
                           "group by m.AccountNumber;")
            temp = cursor.fetchall()
            acc_num=[]
            rev=[]
            for element in temp:
                acc_num.append(element[0])
                rev.append(int(element[1]))
            i = rev.index(max(rev))
            mostrev = [[acc_num[i], rev[i]]]

            print(acc_num,mostrev)
        except:
            return 'Register Fail! Please try again.'

    return render_template('dashboardAdmin6.html', mostrev=mostrev)



@app.route('/d6', methods=['POST', 'GET'])
def d6():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            cursor.execute("select m.AccountNumber, sum(r.BookFee) as total "
                           "from Makes m join Reservation r using(ReservationNumber) "
                           "group by m.AccountNumber;")
            temp = cursor.fetchall()
            acc_num=[]
            rev=[]
            for element in temp:
                acc_num.append(element[0])
                rev.append(int(element[1]))
            i = rev.index(max(rev))
            mostrev = [[acc_num[i], rev[i]]]

            print(acc_num,mostrev)
        except:
            return 'Register Fail! Please try again.'

    return render_template('dashboardAdmin6.html', mostrev=mostrev)


@app.route('/dashboardAdmin7', methods=['POST', 'GET'])
def dashboardAdmin7():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cursor = db.cursor()

    if request.method == 'POST':
        return render_template('dashboardAdmin7.html')
        try:
            cursor.execute("select FlightNumber from Remain where SoldSeat =(select max(SoldSeat) from Remain)")
            flights_list = cursor.fetchall()
            # print(flights_list)
        except:
            return 'Register Fail! Please try again.'

    return render_template('dashboardAdmin7.html', flights_list=flights_list)


@app.route('/d7', methods=['POST', 'GET'])
def d7():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            cursor.execute("select FlightNumber from Remain where SoldSeat =(select max(SoldSeat) from Remain)")
            flights_list = cursor.fetchall()
            # print(flights_list)
        except:
            return 'Register Fail! Please try again.'

    return render_template('dashboardAdmin7.html', flights_list=flights_list)


@app.route('/dashboardAdmin8', methods=['POST', 'GET'])
def dashboardAdmin8():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()

    if request.method == 'POST':
        return render_template('dashboardAdmin8.html')
        try:
            flight_num=request.form['flight_num8']
            cursor.execute("select AccountNumber, FirstName, LastName from Customer "
                           "where AccountNumber in (select AccountNumber from Makes "
                           "where ReservationNumber in (select ReservationNumber from Schedule "
                           "where FlightNumber=%s ))", flight_num)
            cust_info = cursor.fetchall()
            print(cust_info)

        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin8.html', cust_info = cust_info)


@app.route('/d8', methods=['POST', 'GET'])
def d8():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            flight_num=request.form['flight_num8']
            cursor.execute("select AccountNumber, FirstName, LastName from Customer "
                           "where AccountNumber in (select AccountNumber from Makes "
                           "where ReservationNumber in (select ReservationNumber from Schedule "
                           "where FlightNumber=%s ))", flight_num)
            cust_info = cursor.fetchall()
            print(cust_info)

        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin8.html', cust_info = cust_info)


@app.route('/dashboardAdmin9', methods=['POST', 'GET'])
def dashboardAdmin9():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()

    if request.method == 'POST':
        return render_template('dashboardAdmin9.html')
        try:
            airport=request.form['airport9']
            # print(airport)
            cursor.execute("select * from Flight where origin=%s or destination=%s ", (airport,airport))
            flights_info = cursor.fetchall()
            # print(flights_info)


        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin9.html', flights_info = flights_info)

@app.route('/d9', methods=['POST', 'GET'])
def d9():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com","Kocaine","12344321","CS539_Proj" )
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            airport=request.form['airport9']
            # print(airport)
            cursor.execute("select * from Flight where origin=%s or destination=%s ", (airport,airport))
            flights_info = cursor.fetchall()
            # print(flights_info)


        except:
            return 'Search Fail! Please try again.'

    return render_template('dashboardAdmin9.html', flights_info = flights_info)


@app.route('/dashboardAdmin10', methods=['POST', 'GET'])
def dashboardAdmin10():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cursor = db.cursor()

    if request.method == 'POST':
        return render_template('dashboardAdmin10.html')
        try:
            cursor.execute("select FlightNumber, AirportID, ArriveTime, DepartTime "
                           "from StopsAt s join Flight f  using (FlightNumber) "
                           "where timediff(f.originTime, time(s.DepartTime))<>0 "
                           "or timediff(f.destinationTime, time(s.ArriveTime))<>0")
            delayed_list = cursor.fetchall()

            cursor.execute("select FlightNumber, AirportID, ArriveTime, DepartTime "
                           "from StopsAt s join Flight f  using (FlightNumber) "
                           "where timediff(f.originTime, time(s.DepartTime))=0 "
                           "or timediff(f.destinationTime, time(s.ArriveTime))=0")
            ontime_list = cursor.fetchall()

        except:
            return 'Register Fail! Please try again.'

    return render_template('dashboardAdmin10.html', delayed_list=delayed_list, ontime_list=ontime_list)

@app.route('/d10', methods=['POST', 'GET'])
def d10():
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cursor = db.cursor()

    if request.method == 'POST':
        try:
            cursor.execute("select FlightNumber, AirportID, ArriveTime, DepartTime "
                           "from StopsAt s join Flight f  using (FlightNumber) "
                           "where timediff(f.originTime, time(s.DepartTime))<>0 "
                           "or timediff(f.destinationTime, time(s.ArriveTime))<>0")
            delayed_list = cursor.fetchall()

            cursor.execute("select FlightNumber, AirportID, ArriveTime, DepartTime "
                           "from StopsAt s join Flight f  using (FlightNumber) "
                           "where timediff(f.originTime, time(s.DepartTime))=0 "
                           "or timediff(f.destinationTime, time(s.ArriveTime))=0")
            ontime_list = cursor.fetchall()

        except:
            return 'Register Fail! Please try again.'

    return render_template('dashboardAdmin10.html', delayed_list=delayed_list, ontime_list=ontime_list)


def transferFlight(__from__, __to__):
    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cur = db.cursor()

    sql = "select * from Flight f where f.origin = '%s' and f.destination = '%s';"%(__from__, __to__)
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) == 0:
        sql = "select * from Flight f1 cross join Flight f2 where f1.origin='%s' and f2.destination='%s' and timediff(f1.destinationTime, f2.originTime)<0;"%(__from__,__to__)
        cur.execute(sql)
        return cur.fetchall()

    return []



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