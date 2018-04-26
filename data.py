import requests
from conf import *
import json
import re
from requests import RequestException
from db import DB
import datetime

class Spider:
    def __init__(self):
        self.showdata = None
        self.predictData = None
        self.data = None
        self.db = None
        self.toady = None
        self.init()

    def init(self):
        self.data = {}
        self.db = DB()
        self.today = datetime.datetime.now().date()
        self.showdata = dict()
        self.predictData = dict()

    # get source page
    def get_page(self, url, symbol, params):
        url += symbol + '?'
        # construct request url
        for param in params:
            url += param + '=' + params[param] + '&'
        url = url[:-1]
        try:
            res = requests.get(url)
            if res.status_code == 400:
                return None
            html = res.text
            return html
        except RequestException:
            print('request failure')
            # request failed
            return None

    # parse source data
    def parse_page(self,html):
        if html == None:
            return None
        try:
            json.loads(html)
        except ValueError as err:
            return None
        data = json.loads(html)['chart']['result'][0]
        symbol = data['meta']['symbol']
        currency = data['meta']['currency']
        close = data['indicators']['quote'][0]['close']
        open = data['indicators']['quote'][0]['open']
        high = data['indicators']['quote'][0]['high']
        low = data['indicators']['quote'][0]['low']
        volumn = data['indicators']['quote'][0]['volume']
        timestamp = data['timestamp']
        return {
            'symbol': symbol,
            'currency': currency,
            'open':open,
            'high':high,
            'low':low,
            'close': close,
            'volume':volumn,
            'timestamp': timestamp
        }

    def run_ten_real(self):
        for sym in SYMBOLS:
            self.run_one_real(sym)
        return self.predictData

    def run_one_real(self,symbol):
        params = dict(DEFAULT_REAL_PARAMS)
        html = self.get_page(URL, symbol, params)
        if html:
            temp = self.parse_page(html)
            if temp == None:
                return None
            # get index
            index = -1
            for i in range(len(temp['close'])-1, -1, -1):
                if temp['close'][i]:
                    index = i
                    break
            close = temp['close'][index]
            timestamp = temp['timestamp'][index]
            stock_Date_and_Time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            prices = []
            pre = None
            for price in temp['close']:
                if price:
                    prices.append(price)
                    pre = price
                else:
                    prices.append(pre)
            volumes = []
            pre = 0
            for volume in temp['volume']:
                if volume:
                    volumes.append(volume)
                    pre = volume
                else:
                    volumes.append(pre)
            times = list(map(lambda item: datetime.datetime.fromtimestamp(int(item)).strftime('%Y-%m-%d %H:%M:%S').split(' ')[1],temp['timestamp']))
            time = stock_Date_and_Time.split(' ')[1]
            volume = temp['volume'][index]
            row = [symbol, time, close, volume]
            table = 'RealTimePrice'
            if symbol not in self.showdata:
                self.showdata[symbol] = list()
            if symbol not in self.predictData:
                self.predictData[symbol] = list()
            self.predictData[symbol] = list(map(lambda i: [times[i], prices[i], volumes[i]], range(len(times))))
            # print(self.predictData)
            # print(self.predictData)
            tempList = list(map(lambda item: item[0], self.showdata[symbol]))
            if time not in tempList:
                self.showdata[symbol].append([time, close])
            self.data[symbol] = temp
            # self.db.insert(table, row)
            # for i in range(index,-1,-1):
            #     close = temp['close'][i]
            #     timestamp = temp['timestamp'][i]
            #     stock_Date_and_Time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            #     time = stock_Date_and_Time.split(' ')[1]
            #     volume = temp['volume'][i]
            #     row = [symbol, time, close, volume]
            #     table = 'RealTimePrice'
            #     if symbol not in self.showdata:
            #         self.showdata[symbol] = list()
            #     self.showdata[symbol].append([time, close])
            #     print(self.showdata)
            #     self.db.insert(table,row)
            #     self.data[symbol] = temp

    def run_one_history(self,symbol):
        curDate = datetime.datetime.now().date()
        # if curDate == self.toady:
        #     print('today')
        #     return None
        params = dict(DEFAULT_HISTORY_PARAMS)
        html = self.get_page(URL, symbol, params)
        if html:
            temp = self.parse_page(html)
            # get index
            index = -1
            for i in range(len(temp['close'])-1, -1, -1):
                if temp['close'][i]:
                    index = i
                    break
            for i in range(index,-1,-1):
                close = temp['close'][i]
                open = temp['open'][i]
                high = temp['high'][i]
                low = temp['low'][i]
                timestamp = temp['timestamp'][i]
                stock_Date_and_Time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                date = stock_Date_and_Time.split(' ')[0]
                time = stock_Date_and_Time.split(' ')[1]
                volume = temp['volume'][i]
                # print(volume)
                row = [symbol, date, open, high, low, close, volume]
                # print(row)
                table = 'HistoryPrice'
                # self.db.insert(table, row)
                self.toady = curDate


    def run(self):
        #  run run_one_real every 2 minutes
        # run run_one_history every day
        flag = 1
        while True:
            closeTime = datetime.time(16,1,00)
            nowTime = datetime.datetime.now().time()
            # if nowTime > closeTime:
            #     print('stock market has closed')
            #     if flag == 1:
            #         for symbol in SYMBOLS:
            #             self.run_one_history(symbol)
            #         self.db.delete()
            #         flag = 0
            #     continue
            # flag = 1
            for symbol in SYMBOLS:
                self.run_one_real(symbol)
                # self.run_one_history(symbol)


