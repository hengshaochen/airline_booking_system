import pymysql
import datetime

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
        print('True')
        return True
    print('False')
    return False


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
    flag = True

    db = pymysql.connect("kocaine.coua4xtepakf.us-east-2.rds.amazonaws.com", "Kocaine", "12344321", "CS539_Proj")
    cur = db.cursor()
    while True:
        # Monday = 0 , Sunday = 6
        weekday = __date__.weekday()
        weekdayLikeSearch = "%" + str(weekday) + "%"

        sql = "select FlightNumber, NumberOfSeat from Flight where origin='%s' and destination='%s' and WorkingDay like '%s'"%(__from__, __to__, weekdayLikeSearch)
        cur.execute(sql)
        flightInfo = cur.fetchall()
        if 0 == len(flightInfo):
            if True == flag:
                __date__ = __date__ + oneday
                flag = False
            else:
                __date__ = __date__ - oneday
                flag = True
            continue

        for i in range(len(flightInfo)):
            sql = "select * from Remain where FlightNumber='%s' and Date='%s';"%(flightInfo[i][0], __date__)
            cur.execute(sql)
            res = cur.fetchall()

            if 0 == len(res):
                sql = "insert into Remain values('%s', '%s', %d, %d);"%(flightInfo[i][0], __date__, 0, flightInfo[i][1])
                cur.execute(sql)
                db.commit()

        return flightInfo, __date__









print(datetime.date(2018, 12, 31))
oneday = datetime.timedelta(days=1)
print(oneday.days)



print(vagueSearch('PVG', 'SFO', datetime.date(2018, 2, 14), 1))