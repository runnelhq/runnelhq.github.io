# Lauf starten (Environment und Parameter sind optional)
curl -X POST http://127.0.0.1:7300/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"path": "workflows/hello.workflow.yaml", "environment": "prod", "params": {"GREETING": "Moin"}}'

# Ereignisse live verfolgen (Server-Sent Events)
curl -N "http://127.0.0.1:7300/api/v1/events?run=<id>"
