from flask import Flask, render_template, url_for, request, session, redirect
import bcrypt
from flaskext.mysql import MySQL
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
app.config['MYSQL_DATABASE_DB'] = 'CS539_Proj'
app.config['MYSQL_DATABASE_HOST'] = 'kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com:3306'
mysql.init_app(app)


@app.route('/')
def index():

	cur = mysql.get_db().cursor()
	cur.execute('''SELECT data FROM example WHERE id = 1''')
	rv = cur.fetchall()
	return str(rv)


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
    	# 如果user存在，驗證db中的password是否跟使用者輸入的相同
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username and password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
	if request.method == 'POST':
		cursor = conn.cursor()
	
		cursor.execute("INSERT INTO user (user,password)VALUES(%s,%s)",(username,password))
		conn.commit()
		return redirect(url_for('index'))


if __name__ == '__main__':
	app.secret_key = 'mysecret'
	app.run(debug=True)