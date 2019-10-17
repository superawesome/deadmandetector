from flask import Flask, request
from werkzeug.wsgi import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Gauge

app = Flask(__name__)

# adds the prometheus /metrics route
app_dispatch = DispatcherMiddleware(app, {'/metrics': make_wsgi_app()})

g = Gauge('customer_prometheus_watchdog_seconds', "Prometheus Deadman timestamp", ['customer', 'environment'], multiprocess_mode='max')

@app.route('/')
def index():
  return 'Server Works!'

@app.route('/ping', methods=['POST'])
def ping():
    req_data = request.get_json()
    customer = req_data['commonLabels']['customer']
    environment = req_data['commonLabels']['environment']
    key = "{}:{}".format(customer, environment)
    g.labels(customer, environment).set_to_current_time()
    return '{} - {}\n'.format(key, g.labels(customer, environment)._value.get())
