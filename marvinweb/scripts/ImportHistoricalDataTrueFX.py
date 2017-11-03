###############################################################################
#
# Script to extract tick tick data from source file and
#
# Uses Python 3.4
#
###############################################################################

import csv
import os
import sys
import zipfile

import mysql.connector


def getAllFilesFromDir(rootdir, ext):
    """
    Extracts all files in rootdir with a given extension
    :param rootdir:
    :param ext:
    :return:
    """
    files = []

    for root, dirs, files in os.walk(rootdir):
        for file in sorted(files):
            if file.endswith('.{}'.format(ext)):
                files.append(file)

    return files


def unzipIntoTempLocation(files, tempfolder):
    """
    takes a list of zip files and unzips them  into a given temp folder
    :param files:
    :param tempfolder: temp folder to put extracted files
    :return:
    """
    for file in files:
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(tempfolder)


def deleteFilesFromTempLocation(tempfolder):
    """
    Given a folder location delete all the files in there
    :param temp file path:
    :return:
    """
    for file in os.scandir(tempfolder):
        if file.is_file():
            os.remove(os.path.join(tempfolder, file))


def convertToDBTimeStamp(ts) -> str:
    """
    Given a timestamp in the format yyyymmdd HH:MM:ss.SSS convert to yyyy-mm-dd HH:MM:ss.SSS
    :param pretimestamp:
    :return:
    """
    return ts[:4] + '-' + ts[4:6] + '-' + ts[6:]


def insertRowsIntDB(size, data):
    cnx = mysql.connector.connect(user='marvinadmin', password='adminmarvin',
                                  host='127.0.0.1',
                                  database='marvin_db')
    cursor = cnx.cursor()

    add_ticks = ("INSERT INTO eurusdtickdata "
                 "(timestamp, bid, ask) "
                 "VALUES ")
    add_ticks = add_ticks + "(%s, %s, %s)," * size
    add_ticks = add_ticks[:-1]

    # Insert tick data
    cursor.execute(add_ticks, data)
    emp_no = cursor.lastrowid

    cnx.commit()
    cursor.close()
    cnx.close()


def deleteDaysDataFromDb(file):
    tokens = file.split('-')
    year = tokens[1]
    month = tokens[2][:2]
    startDate = "{}-{}-01 00:00:00.000".format(year, month)
    nextmonth = int(month) + 1
    nextyear = int(year)
    if (nextmonth > 12):
        nextmonth = 1
        nextyear = nextyear + 1
    endDate = "{}-{}-01 00:00:00.000".format(nextyear, nextmonth)

    cnx = mysql.connector.connect(user='marvinadmin', password='adminmarvin',
                                  host='127.0.0.1',
                                  database='marvin_db')
    cursor = cnx.cursor()

    delete_ticks = ("DELETE FROM eurusdtickdata where timestamp >= %s and timestamp < %s")
    # delete tick data
    cursor.execute(delete_ticks, (startDate, endDate))
    emp_no = cursor.lastrowid

    cnx.commit()
    cursor.close()
    cnx.close()


def insertCsVDataIntoDB(tempdir):
    """
    Traverse files in given directory and insert them into the DB
    the datetime value must be converted from
    20090514 06:42:50.514 to
    2009-05-14 06:42:50.514

    :param tempdir: the directory from where to get the files
    :return: None
    """

    # run through files in order and input data into the DB
    for root, dirs, files in os.walk(tempdir):
        for file in sorted(files):
            if file.endswith(".csv"):
                deleteDaysDataFromDb(file)
                with open(os.path.join(tempdir, file), 'r') as f:
                    r = csv.reader(f)
                    f.seek(0)  # <-- set the iterator to beginning of the input file
                    counter = 0
                    data = ()
                    for row in r:
                        timestamp = convertToDBTimeStamp(row[1])
                        bid = row[2]
                        ask = row[3]
                        data = data + (timestamp, bid, ask)
                        counter += 1
                        if counter % 20 == 0:
                            insertRowsIntDB(counter, data)
                            counter = 0
                            data = ()
                    insertRowsIntDB(counter, data)


if __name__ == '__main__':
    numCommandArgs = len(sys.argv)
    if numCommandArgs > 1:
        print("TODO: do something with the args")

    files = getAllFilesFromDir('D:/mktdata/TrueFX/', 'zip')
    tempdir = "D:/TEMP"
    # unzipIntoTempLocation(files, tempdir)
    insertCsVDataIntoDB(tempdir)
    # deleteFilesFromTempLocation(tempdir)
