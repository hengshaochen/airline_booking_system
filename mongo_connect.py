from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restaurant_pos'
app.config['MONGO_URI'] = 'mongodb://henry:abc794613@ds111059.mlab.com:11059/restaurant_pos'

mongo = PyMongo(app)

@app.route('/')
def index():
	if 'username' in session:
		return render_template('dashboard.html')
	return render_template('index.html')

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
		users = mongo.db.users
		existing_user = users.find_one({'name' : request.form['username']})

		if existing_user is None:
			hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
			users.insert({'name' : request.form['username'], 'password' : hashpass})
			session['username'] = request.form['username']
			return redirect(url_for('index'))

		return 'That username already exists!'

	# if not POST, then it is GET
	return render_template('register.html')

if __name__ == '__main__':
	app.secret_key = 'mysecret'
	app.run(debug=True)