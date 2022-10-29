from datetime import datetime
import io
import os

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl
from flask import Flask, make_response, render_template, request, send_file
import sqlite3

db_path = '/home/pi/temperature/'
app = Flask(__name__)
font = {'size': 20}
mpl.rc('font', **font)
mpl.rcParams['figure.figsize'] = (20, 18)
#mpl.rcParams['date.autoformatter.minute'] = '%Y-%m-%d %H:%M:%S'


def get_last_data(): 
    with sqlite3.connect(os.path.join(db_path, 'sensor_data.db')) as conn:
        curs = conn.cursor()
        for row in curs.execute('select * from DHT_data order by timestamp desc limit 1'):
            time = str(row[0])
            temp = row[1]
            hum = row[2]
    return time, temp, hum


def get_hist_data(num_samples):
    with sqlite3.connect(os.path.join(db_path, 'sensor_data.db')) as conn:
        curs = conn.cursor()
        curs.execute('select * from DHT_data order by timestamp desc limit ' + str(num_samples))
        data = curs.fetchall()
    dates = []
    temps = []
    hums = []
    for row in reversed(data):
        dates.append(row[0])
        temps.append(row[1])
        hums.append(row[2])
    return dates, temps, hums


def max_rows_table():
    with sqlite3.connect(os.path.join(db_path, 'sensor_data.db')) as conn:
        curs = conn.cursor()
        for row in curs.execute('select count(temp) from DHT_data'):
            max_number_rows = row[0]
    return max_number_rows


global num_samples
num_samples = min(100, max_rows_table())


@app.route('/')
def index():
    time, temp, hum = get_last_data()
    template_data = {
        'time': time,
        'temp': temp,
        'hum': hum,
        'num_samples': num_samples
    }
    return render_template('index.html', **template_data)


@app.route('/', methods=['POST'])
def my_form_post():
    global num_samples
    num_samples = int (request.form['num_samples'])
    num_max_samples = max_rows_table()
    if (num_samples > num_max_samples):
        num_samples = num_max_samples - 1
    time, temp, hum = get_last_data()
    template_data = {
        'time': time,
        'temp': temp,
        'hum': hum,
        'num_samples': num_samples
    }
    return render_template('index.html', **template_data)


@app.route('/plot/temp')
def plot_temp():
    times, temps, hums = get_hist_data(num_samples)
    times = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in times]
    ys = temps
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title('Temperature [°C]')
    axis.set_xlabel('Samples')
    axis.grid(True)
    xs = times
    axis.plot(xs, ys)
    fig.autofmt_xdate(rotation=90, ha='center')
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route('/plot/hum')
def plot_hum():
    times, temps, hums = get_hist_data(num_samples)
    times = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in times]
    ys = hums
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title('Humidity [%]')
    axis.set_xlabel('Samples')
    axis.grid(True)
    xs = times
    axis.plot(xs, ys)
    fig.autofmt_xdate(rotation=90, ha='center')
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0' , port=80, debug=False)
