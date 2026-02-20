#!/bin/bash

# Test curl command for audit log webhook
# This sends a sample audit log event to the webhook server

curl -X POST http://127.0.0.1:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-17 14:30:45.123 -0500",
    "application": "mrbeta.m3globalresearch.com",
    "ipaddr": "192.168.123.234",
    "userid": "userabc123",
    "result": true,
    "eventtype": "login",
    "message": {
      "detail": "User attempted password reset"
    }
  }'

echo ""
echo "Webhook sent!"
