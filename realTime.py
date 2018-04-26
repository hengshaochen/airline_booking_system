from sklearn import linear_model
import pymysql
from flaskext.mysql import MySQL
conn = pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com","ryan","11111111","stock" )

def show():
	data = []
	data.append(['00:00:00', 123])
	data.append(['00:01:00', 140])
	data.append(['00:02:00', 140])
	data.append(['00:03:00', 0])
	data.append(['00:04:00', 140])
	data.append(['00:05:00', 185])
	return data