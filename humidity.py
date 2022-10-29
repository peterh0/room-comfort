import datetime
import time

import board
import adafruit_dht
import sqlite3

sample_freq = 15*60 # seconds * 60 = minutes
dbname = 'sensor_data.db'

DHT_SENSOR = adafruit_dht.DHT22(board.D4)
DHT_PIN = 4


def get_data():
    try:
        temperature = DHT_SENSOR.temperature
        humidity = DHT_SENSOR.humidity
#        print('Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature, humidity))
        return temperature, humidity
    except RuntimeError as error:
        print(f'RuntimeError: {error.args[0]}')
    except Exception as error:
        print(f'Exception: {error}')
        DHT_SENSOR.exit()
        raise error
    return -99, -99

def get_data2():
    return 1, 2


def log_data(temperature, humidity):
    dtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    curs.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?))", (temperature, humidity))
    conn.commit()
    conn.close()


def display_data():
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()
    for row in curs.execute('select * from DHT_data'):
        print(row)
    conn.close()

def main():
    while True:
        temperature, humidity = get_data2()
        if temperature != -99:
            log_data(temperature, humidity)
        time.sleep(sample_freq)

main()

