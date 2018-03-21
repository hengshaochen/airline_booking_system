from flask import Flask, render_template, url_for, request, session, redirect
import bcrypt
import pymysql
from flaskext.mysql import MySQL
import sys
#import MySQLdb


app = Flask(__name__)
#app.config['MONGO_DBNAME'] = 'restaurant_pos'
#app.config['MONGO_URI'] = 'mongodb://henry:abc794613@ds111059.mlab.com:11059/restaurant_pos'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://henrychen0702:Abc794613@henrychen0702.cqdz4l9ywfoh.us-east-2.rds.amazonaws.com:3306/airlines' #这里登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名text1
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True #设置这一项是每次请求结束后都会自动提交数据库中的变动

#conn = MySQL.connect(host="henrychen0702.cqdz4l9ywfoh.us-east-2.rds.amazonaws.com:3306/airlines",user="henrychen0702",password="Abc794613",db="airlines")

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'Kocaine'
app.config['MYSQL_DATABASE_PASSWORD'] = '12344321'
app.config['MYSQL_DATABASE_DB'] = 'airlines'
app.config['MYSQL_DATABASE_HOST'] = 'kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com'
mysql.init_app(app)


@app.route('/')
def index():
	if 'username' in session:
		return render_template('dashboardUser.html')
	return render_template('index.html')

	#cur = mysql.get_db().cursor()
	#cur.execute('''SELECT * FROM account''')
	#rv = cur.fetchall()
	#return str(rv)


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
			#print('Hello world!', file=sys.stderr)
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


if __name__ == '__main__':
	app.secret_key = 'mysecret'
	app.run(debug=True)