from flask import Flask, request, render_template
from datetime import datetime, timedelta
from werkzeug.wsgi import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Gauge
import time


app = Flask(__name__)

# adds the prometheus /metrics route
app_dispatch = DispatcherMiddleware(app, {'/metrics': make_wsgi_app()})

gauges = {}

@app.route('/')
def index():
  return 'Server Works!'

@app.route('/ping', methods=['POST'])
def ping():
    customer = request.form['customer']
    environment = request.form['environment']
    key = "{}:{}".format(customer, environment)
    try: # update existing Gauge
        gauges[key].set_to_current_time()
    except KeyError: # Gauge doesn't exist yet, create then update it
        gauges[key] = Gauge(key, 'Prometheus Deadman timestamp', multiprocess_mode='max')
        gauges[key].set_to_current_time()
    return '{} - {}\n'.format(key, gauges[key]._value.get())

@app.route('/list')
def list():
    curtime = datetime.now()
    return render_template('list.html', curtime=curtime, status=gauges)

@app.template_filter('dt')
def _jinja2_filter_datetime(t):
    return time.ctime(t)
