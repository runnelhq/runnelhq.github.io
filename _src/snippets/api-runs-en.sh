# start a run (environment and parameters are optional)
curl -X POST http://127.0.0.1:7300/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"path": "workflows/hello.workflow.yaml", "environment": "prod", "params": {"GREETING": "Moin"}}'

# follow events live (server-sent events)
curl -N "http://127.0.0.1:7300/api/v1/events?run=<id>"
