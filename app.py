from flask import Flask, request, render_template
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import logging
from alertmanager import Alert, AlertManager


app = Flask(__name__)

status = {}

def check_status():
    for key in status.keys():
        customer, environment = key.split(':')
        last_reported = status[key]
        if (datetime.now() - last_reported).total_seconds() > 30:
            logging.info("deadman expired: {} - {}, last reported on {}, current time is {}".format(customer, environment, last_reported, datetime.now()))
            data = {
                    "labels": {
                        "alertname": "Deadman Alert",
                        "customer": customer,
                        "environment": environment,
                        "severity": "critical",
                        "name": "{} - {} - Prometheus not responding".format(customer, environment)
                    },
                    "annotations": {
                        "description": "Prometheus not responding",
                        "summary": "Prometheus not responding"
                    }
                    }
            a = Alert.from_dict(data)
            am = AlertManager(host="http://18.191.186.205")
            am.post_alerts(a)


logging.basicConfig()

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_status, trigger="interval", seconds=30)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def index():
  return 'Server Works!'

@app.route('/ping', methods=['POST'])
def ping():
    timestamp = datetime.now()
    customer = request.form['customer']
    environment = request.form['environment']
    key = "{}:{}".format(customer, environment)
    status[key] = timestamp
    return 'OK\n'

@app.route('/list')
def list():
    curtime = datetime.now()
    return render_template('list.html', curtime=curtime, status=status)



