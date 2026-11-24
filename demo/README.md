# Local observability lab

A standalone Prometheus, Alertmanager, Grafana and Blackbox Exporter exercise. The original root configuration is not used; no production address, Telegram token or external target is needed. All published ports bind to loopback only. The nginx target and monitoring services are disposable local containers.

## Run

```bash
cd demo
read -rs -p 'Choose a local Grafana password: ' GRAFANA_ADMIN_PASSWORD
echo
export GRAFANA_ADMIN_PASSWORD
docker compose -p potato-metrics-demo config --quiet
docker compose -p potato-metrics-demo up -d
```

Open Prometheus at http://127.0.0.1:9090, Alertmanager at http://127.0.0.1:9093 and Grafana at http://127.0.0.1:3000. The Grafana datasource is provisioned; login is admin and the password supplied above on first initialization. A previously initialized demo volume retains its own password.

## Exercise

Query `probe_success{job="blackbox"}` in Prometheus. Expect 1 once all services are ready. Stop only the disposable target:

```bash
docker compose -p potato-metrics-demo stop demo-target
```

After the probe fails and the 30-second rule duration elapses, expect DemoTargetUnavailable to fire. Restart the target to observe recovery.

```bash
docker compose -p potato-metrics-demo start demo-target
docker compose -p potato-metrics-demo down
unset GRAFANA_ADMIN_PASSWORD
```

The lab has no external notification receiver, real SLA, production hardening claim or production log collector. The commands above are expected behavior, not measured results until CI or a local run confirms them. The root stack is historical and not a safe default; do not run it as part of this lab.

## Dashboard and synthetic logs

Open the provisioned **Potato Metrics | Local lab** dashboard in Grafana. It displays HTTP probe state, duration, firing alerts, and synthetic logs. Run `python3 emit_demo_log.py` from `demo/` to send a generated event to local Loki and verify retrieval. The exercise deliberately uses no host logs, Docker socket, customer data or external telemetry. This is a local ingestion example, not a production log collection agent.
