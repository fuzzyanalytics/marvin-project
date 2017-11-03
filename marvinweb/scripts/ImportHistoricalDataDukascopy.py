###############################################################################
#
# Script to extract tick tick data from source file and
#
# Uses Python 3.4
#
###############################################################################

import csv
import errno
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from subprocess import call

import mysql.connector

CCYPAIR = "EURUSD"


def insertRowsIntDB(size, data):
    cnx = mysql.connector.connect(user='marvinadmin', password='adminmarvin',
                                  host='127.0.0.1',
                                  database='marvin_db')
    cursor = cnx.cursor()

    add_ticks = ("INSERT INTO dukaeurusdtick "
                 "(timestamp, bid, ask, bid_volume, ask_volume) "
                 "VALUES ")
    add_ticks = add_ticks + "(%s, %s, %s, %s, %s)," * size
    add_ticks = add_ticks[:-1]

    # Insert tick data
    cursor.execute(add_ticks, data)
    emp_no = cursor.lastrowid

    cnx.commit()
    cursor.close()
    cnx.close()


def deleteDaysDataFromDb(dt):
    """
    given a date, remove data from the DB from that date
    :param dt:
    :return:
    """

    year = dt.year
    month = dt.month
    day = dt.day
    startDate = "{} 00:00:00.000".format(dt.strftime("%Y-%m-%d"))
    tomorrow = dt + timedelta(days=1)
    endDate = "{} 00:00:00.000".format(tomorrow.strftime("%Y-%m-%d"))

    cnx = mysql.connector.connect(user='marvinadmin', password='adminmarvin',
                                  host='127.0.0.1',
                                  database='marvin_db')
    cursor = cnx.cursor()

    delete_ticks = ("DELETE FROM dukaeurusdtick where timestamp >= %s and timestamp < %s")
    # delete tick data
    cursor.execute(delete_ticks, (startDate, endDate))
    emp_no = cursor.lastrowid

    cnx.commit()
    cursor.close()
    cnx.close()


def insertDataIntoDB(dt, file):
    """
    Given the full path to a file insert contents them into the DB
    Data from the same date is also deleted first from the DB
    :param dt: the date of the data which is to be uploaded
    :param file: the full path to the file to upload
    :return: None
    """

    # run through files in order and input data into the DB
    if file.endswith(".csv"):
        deleteDaysDataFromDb(dt)
        with open(file, 'r') as f:
            r = csv.reader(f)
            f.seek(0)  # <-- set the iterator to beginning of the input file
            counter = 0
            totalcounter = 0
            data = ()
            for row in r:
                if len(row) > 0 and row[0] != "time":
                    timestamp = row[0]
                    bid = row[1]
                    ask = row[2]
                    bid_volume = row[3]
                    ask_volume = row[4]
                    data = data + (timestamp, bid, ask, bid_volume, ask_volume)
                    counter += 1
                    totalcounter += 1
                    if counter % 20 == 0:
                        # print("total counter {}\n".format(totalcounter))
                        insertRowsIntDB(counter, data)
                        counter = 0
                        data = ()
                else:
                    # skip
                    pass
            # insert final rows
            # print("total counter {}".format(totalcounter))
            # if there are exactly N % 20 rows then we have nothing else to BCP in
            if (counter > 0):
                insertRowsIntDB(counter, data)


def downloadDateRangeAndInsertIntoDB(startDate, endDate, tempDir) -> None:
    # this will give you a list containing all of the dates
    dd = [startDate + timedelta(days=x) for x in range((endDate - startDate).days + 1)]

    for dt in dd:
        print(dt)
        args = "{} -s {} -e {} -f {} --header".format(CCYPAIR, dt, dt, tempDir)
        # e.g. EURUSD-2017_10_01-2017_10_01
        dtUnderBars = dt.strftime('%Y_%m_%d')
        filename = "{}-{}-{}.csv".format(CCYPAIR, dtUnderBars, dtUnderBars)
        sts = call("duka " + args)
        # deleteDaysDataFromDb(dt)
        fullpath = os.path.join(tempDir, filename)
        duka_data_file = Path(fullpath)
        if duka_data_file.exists():
            insertDataIntoDB(dt, fullpath)
            # os.remove(fullpath)
            print()
        else:
            print("!! {} does not exist".format(fullpath))


def printUsageStr() -> None:
    """
    Prints the usage string of this utility.
    :return: None
    """
    print("Usage: ImportHistoricalDataDukascopy StartDate EndDate");
    print("*      StartDate and EndDate should be in format YYYYMMDD");
    print("*      EndDate should come after StartDate");


if __name__ == '__main__':
    numCommandArgs = len(sys.argv)
    if numCommandArgs <= 1:
        printUsageStr()
        exit(1)

    startDateStr = sys.argv[1]
    endDateStr = sys.argv[2]

    pattern = re.compile(r"^[0-9]{8}$")
    matchStart = pattern.match(startDateStr)
    matchEnd = pattern.match(endDateStr)
    if not matchStart:
        print("Error. StartDate in wrong format")
        printUsageStr()
        exit(1)
    if not matchEnd:
        print("Error. EndDate in wrong format")
        printUsageStr()
        exit(1)
    if int(startDateStr) > int(endDateStr):
        print("Error: EndDate is before StartDate")
        printUsageStr()
        exit(1)

    tempDir = "D:\\MKTDATA\\Dukascopy\\"

    try:
        os.makedirs(tempDir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    startDate = date(int(startDateStr[0:4]), int(startDateStr[4:6]), int(startDateStr[6:8]))
    endDate = date(int(endDateStr[0:4]), int(endDateStr[4:6]), int(endDateStr[6:8]))

    downloadDateRangeAndInsertIntoDB(startDate, endDate, tempDir)
