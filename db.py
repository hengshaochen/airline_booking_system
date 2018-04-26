import pymysql
import datetime


class DB:
    def __init__(self):
        self.db = None
        self.today = None
        self.init()

    def init(self):
        self.today = datetime.datetime.now().date()
        self.connect()

    # connect to database
    def connect(self):
        times = 0
        N = 10
        while times < N:
            try:
                self.db = pymysql.connect("class568.cgzotjrssahz.us-east-1.rds.amazonaws.com", "ryan", "11111111", "stock")
                break
            except:
                print('hh')
                times += 1

    # insert one row in related table
    def insert(self, tableName, row):
        sql = 'insert into ' + tableName + ' values('
        for item in row:
            sql += repr(item) + ','
        sql = sql[:-1]
        sql += ');'
        print(sql)
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            cursor.close()
        except:
            self.db.rollback()

    # delete all data in realtime table
    def delete_realtime(self):
        cur = datetime.datetime.now().date()
        if cur == self.today:
            return None
        sql = 'delete from RealTimePrice;'
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            cursor.close()
        except:
            print('hhh')
            self.db.rollback()
        finally:
            self.today = cur

    # delete all data in history table
    def delete_history(self):
        cur = datetime.datetime.now().date()
        if cur == self.today:
            return None
        earliest_date = str(datetime.date(cur.year - 1, cur.month, cur.day))
        sql = 'delete from HistoryPrice where historyTime < {};'.format(earliest_date)
        print(sql)
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            cursor.close()
        except:
            print('hhh')
            self.db.rollback()
        finally:
            self.today = cur

    def delete(self):
        self.delete_realtime()
        self.delete_history()

if __name__ == '__main__':
    db = DB()
    # table = 'HistoryPrice'
    # row = ['sys-0','2017-10-09','27','89','128','21','1321']
    # db.insert(table,row)
    # table = 'RealTimePrice'
    # row = ['sys-0', '23:12:12', '80','1208']
    # db.insert(table,row)
    db.delete()

