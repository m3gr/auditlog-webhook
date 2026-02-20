# Test valid payload
echo "Testing valid audit log event..."
curl -X POST http://localhost:8080 \
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

echo -e "\n\n"

# Test invalid event type
echo "Testing invalid event type (should fail)..."
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-17 14:30:45.123 -0500",
    "application": "mrbeta.m3globalresearch.com",
    "ipaddr": "192.168.123.234",
    "userid": "userabc123",
    "result": true,
    "eventtype": "invalid_event",
    "message": {
      "detail": "This should fail validation"
    }
  }'

echo -e "\n\n"

# Test missing required field
echo "Testing missing required field (should fail)..."
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-17 14:30:45.123 -0500",
    "application": "mrbeta.m3globalresearch.com",
    "ipaddr": "192.168.123.234",
    "result": true,
    "eventtype": "login",
    "message": {
      "detail": "Missing userid field"
    }
  }'

echo -e "\n\n"

# Test invalid IP address format
echo "Testing invalid IP address format (should fail)..."
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-17 14:30:45.123 -0500",
    "application": "mrbeta.m3globalresearch.com",
    "ipaddr": "invalid.ip.address",
    "userid": "userabc123",
    "result": true,
    "eventtype": "login",
    "message": {
      "detail": "Invalid IP format"
    }
  }'

echo -e "\n\n"
echo "Validation tests completed!"
