# Deadman Switch Detector for Prometheus

This project is intended to complement a Prometheus monitoring system.

The goal is to provide the backend for detecting failed Prometheus instances, for systems where those instances cannot easily be monitored by others. Specifically, for the case where remote Prometheus instances can egress to an AlertManager, but we cannot easily ingress to monitor the health of those Prometheus instances. Those Prometheus instances can send a "deadman" alert that is always firing, and we can passively watch to make sure those alerts don't stop.

This project receives those alerts from the AlertManager, and acts as a prometheus exporter, exporting the timestamp of the last-received "deadman" alert from each remote instance.

Remote instances are grouped based on 2 Labels- "customer" and "environment".


NOTE: This detector does not save its state anywhere other than in-memory! If it's restarted, it will forget about all previously-received alerts. That means if you restart it while a remote Prometheus is down, there will not be any alert generated for that instance! This will likely be improved in future versions.

You can manually inject entries (with the current timestamp) like this:
```shell
curl -v -H "Content-Type: application/json" localhost:54306/ping -d '{"commonLabels":{"customer":"test","environment":"testcluster"}}'
```


The remote Prometheus instances should be configured to send an alert like this:

```yaml
- alert: DeadManBoy
  expr: vector(1)
  labels:
    customer: "{{ cluster_customer }}"
    environment: "{{ cluster_name }}"
    severity: deadman
    product: prometheus
  annotations:
    description: "Prometheus Watchdog - should always be firing"
```

The AlertManager should be configured to receive those alerts and send them to this deadman detector:

```yaml
receivers:
- name: deadmansswitch
  webhook_configs:
  - send_resolved: false
    url: http://<host>:<port>/ping
route:
  routes:
  - receiver: deadmansswitch
    group_by:
    - '...'
    group_interval: 1s
    group_wait: 0s
    match:
      severity: deadman
    repeat_interval: 15s
```

The local Prometheus should scrape this deadman detector, and fire an alert back to the AM if any of the monitored instances haven't reported recently:

```yaml
scrape_configs:
  - job_name: deadman
    metrics_path: /metrics
    scheme: http
    static_configs:
    - labels:
        class: production
        customer: opserv
        environment: opserv
        product: deadman
      targets:
      - <host>:<port>

groups:
- name: Deadman Rules
  rules:
  - alert: DeadPrometheus
    annotations:
      description: Prometheus seems dead
    expr: time() - customer_prometheus_watchdog_seconds > 50
    labels:
      name: prometheus_not_responding
      product: prometheus
      severity: critical
```
