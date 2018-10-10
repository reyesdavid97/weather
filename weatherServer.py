# by David Reyes
import socket
from _thread import *
import threading
import requests
import time
import sqlite3
from sqlite3 import Error


def create_database_connection(db_file):
    try:
        db_conn = sqlite3.connect(db_file)
        print("Database connection created. \nSQLite version: " + sqlite3.version)
        return db_conn
    except Error as e:
        print(e)

    return None


def create_table(db_conn, create_table_sql):
    try:
        c = db_conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_weather(db_conn, weather_data):
    sql = """ INSERT INTO weather(name,time,info)
              VALUES(?,?,?) """
    cur = db_conn.cursor()
    cur.execute(sql, weather_data)
    return cur.lastrowid


def thread(conn):
    while True:
        city = conn.recv(BUFFER_SIZE)
        if not city:
            print("Exiting.")
            lock.release()
            break

        db_conn = create_database_connection(DB_FILE)
        if db_conn is not None:
            create_table(db_conn, SQL_CREATE_WEATHER_TABLE)
        else:
            print("Error, could not create database connection.")

        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=5442fa42aef4380302b6e687cdffda8c'
        r = requests.get(url.format(city.decode('utf-8'))).json()

        name = city.decode('utf-8')
        weather_info = "\nCity: " + name
        weather_info += "\nWeather: " + str(r['weather'][0]['main'])
        weather_info += "\nDescription: " + str(r['weather'][0]['description'])
        weather_info += "\nTemperature: " + str(r['main']['temp']) + " F"
        weather_info += "\nPressure: " + str(r['main']['pressure'])
        weather_info += "\nHumidity: " + str(r['main']['humidity'])

        info = (name, str(time.time()), weather_info)
        create_weather(db_conn, info)

        conn.sendall(weather_info.encode('utf-8'))

    db_conn.close()
    conn.close()


lock = threading.Lock()
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 5000
DB_FILE = 'weatherDB.db'
SQL_CREATE_WEATHER_TABLE = """ CREATE TABLE IF NOT EXISTS weather (
                                name text PRIMARY KEY,
                                time integer, 
                                info text
                               ); """

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
print("Socket bound to port: " + str(TCP_PORT))
s.listen(10)
print("Socket is listening.")

while True:
    connection, address = s.accept()
    lock.acquire()
    start_new_thread(thread, (connection, ))
