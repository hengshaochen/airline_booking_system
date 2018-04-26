URL = 'https://query1.finance.yahoo.com/v8/finance/chart/'
SYMBOLS = ['GOOG','AABA','VMW','BABA','HPQ','AAPL','AMZN','FB','IBM','SNAP']
DEFAULT_REAL_PARAMS = {
        'range': '1d',
        'includePrePost': 'false',
        'interval': '1m',
        'corsDomain': 'finance.yahoo.com',
        '.tsrc': 'finance'
    }

DEFAULT_HISTORY_PARAMS = {
    'formatted':'true',
    'crumb':'S7Z32GyvUii',
    'lang':'en-US',
    'region':'US',
    'interval':'1d',
    'events':'div|split',
    'range':'1y',
    'corsDomain':'finance.yahoo.com'
}

PROXY_POOL_URL = 'http://localhost:5555/random'
DEFAULT_HEADERS = {
            'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.168 Safari/537.36',
        }
