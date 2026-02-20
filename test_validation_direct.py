#!/usr/bin/env python
"""Test script to verify validation is working."""

import json
import sys
sys.path.insert(0, 'src')

from main import validate_audit_log, AUDIT_LOG_SCHEMA

# Test valid payload
valid_payload = {
    "date": "2026-02-17 14:30:45.123 -0500",
    "application": "test.com",
    "ipaddr": "192.168.1.1",
    "userid": "user1",
    "result": True,
    "eventtype": "login",
    "message": {"detail": "test"}
}

# Test invalid eventtype
invalid_payload = {
    "date": "2026-02-17 14:30:45.123 -0500",
    "application": "test.com",
    "ipaddr": "192.168.1.1",
    "userid": "user1",
    "result": True,
    "eventtype": "INVALID",
    "message": {"detail": "test"}
}

# Test missing field
missing_field = {
    "date": "2026-02-17 14:30:45.123 -0500",
    "application": "test.com",
    "ipaddr": "192.168.1.1",
    "result": True,
    "eventtype": "login",
    "message": {"detail": "test"}
}

print("Testing validation function...")
print("\nSchema:")
print(json.dumps(AUDIT_LOG_SCHEMA, indent=2))

print("\n1. Testing valid payload:")
is_valid, error = validate_audit_log(valid_payload)
print(f"   Result: {'PASS' if is_valid else 'FAIL'}")
if error:
    print(f"   Error: {error}")

print("\n2. Testing invalid eventtype (should FAIL):")
is_valid, error = validate_audit_log(invalid_payload)
print(f"   Result: {'PASS' if is_valid else 'FAIL'}")
if error:
    print(f"   Error: {error}")

print("\n3. Testing missing required field (should FAIL):")
is_valid, error = validate_audit_log(missing_field)
print(f"   Result: {'PASS' if is_valid else 'FAIL'}")
if error:
    print(f"   Error: {error}")
