"""Main module for audit log webhook."""

import json
import time
import threading
from queue import Queue
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
import requests
from jsonschema import validate, ValidationError


# CloudWatch configuration
LOG_GROUP_NAME = 'appl_audit_log'
LOG_STREAM_NAME = f'webhook-{datetime.now().strftime("%Y-%m-%d")}'

# JSON Schema for audit log events
AUDIT_LOG_SCHEMA = {
    "type": "object",
    "required": ["date", "application", "ipaddr", "userid", "result", "eventtype", "message"],
    "properties": {
        "date": {
            "type": "string",
            "pattern": "^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}\\.\\d{3} [+-]\\d{4}$"
        },
        "application": {
            "type": "string"
        },
        "ipaddr": {
            "type": "string",
            "pattern": "^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$"
        },
        "userid": {
            "type": "string"
        },
        "result": {
            "type": "boolean"
        },
        "eventtype": {
            "type": "string",
            "enum": ["login", "password_change", "acl_change"]
        },
        "message": {
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string"
                }
            }
        }
    },
    "additionalProperties": False
}

# Global CloudWatch client and queue
cloudwatch_client = None
sequence_token = None
log_queue = Queue()
worker_thread = None
shutdown_event = threading.Event()
error_flag = False


def setup_cloudwatch_log_group():
    """Create CloudWatch log group and stream if they don't exist."""
    global cloudwatch_client, sequence_token, error_flag
    
    try:
        cloudwatch_client = boto3.client('logs', region_name='us-east-1')
        
        # Create log group if it doesn't exist
        try:
            cloudwatch_client.create_log_group(logGroupName=LOG_GROUP_NAME)
            print(f"Created CloudWatch log group: {LOG_GROUP_NAME}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                print(f"CloudWatch log group already exists: {LOG_GROUP_NAME}")
            else:
                error_flag = True
                raise
        
        # Create log stream if it doesn't exist
        try:
            cloudwatch_client.create_log_stream(
                logGroupName=LOG_GROUP_NAME,
                logStreamName=LOG_STREAM_NAME
            )
            print(f"Created CloudWatch log stream: {LOG_STREAM_NAME}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                print(f"CloudWatch log stream already exists: {LOG_STREAM_NAME}")
                # Get the sequence token for existing stream
                response = cloudwatch_client.describe_log_streams(
                    logGroupName=LOG_GROUP_NAME,
                    logStreamNamePrefix=LOG_STREAM_NAME
                )
                if response['logStreams']:
                    sequence_token = response['logStreams'][0].get('uploadSequenceToken')
            else:
                error_flag = True
                raise
        
        print(f"CloudWatch logging configured successfully")
        
    except Exception as e:
        print(f"Error setting up CloudWatch: {str(e)}")
        print("Continuing without CloudWatch logging...")
        error_flag = True


def cloudwatch_worker():
    """Background worker thread that processes CloudWatch log queue."""
    global cloudwatch_client, sequence_token, error_flag
    
    print("CloudWatch worker thread started")
    
    while not shutdown_event.is_set() or not log_queue.empty():
        try:
            # Wait for log event with timeout to check shutdown flag
            try:
                log_data = log_queue.get(timeout=0.5)
            except:
                continue
            
            if log_data is None or not cloudwatch_client:
                log_queue.task_done()
                continue
            
            message, payload = log_data
            
            print(f"Processing CloudWatch event: {message}")
            
            # Prepare log event
            log_event = {
                'timestamp': int(time.time() * 1000),
                'message': message
            }
            
            if payload:
                log_event['message'] = f"{message}\n{json.dumps(payload, indent=2)}"
            
            kwargs = {
                'logGroupName': LOG_GROUP_NAME,
                'logStreamName': LOG_STREAM_NAME,
                'logEvents': [log_event]
            }
            
            if sequence_token:
                kwargs['sequenceToken'] = sequence_token
            
            response = cloudwatch_client.put_log_events(**kwargs)
            sequence_token = response.get('nextSequenceToken')
            
            print(f"Successfully sent to CloudWatch")
            log_queue.task_done()
            
        except Exception as e:
            print(f"Error in CloudWatch worker: {str(e)}")
            log_queue.task_done()
            error_flag = True


def validate_audit_log(payload: Dict[str, Any]):
    """Validate audit log payload against schema.
    
    Args:
        payload: The JSON payload to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        validate(instance=payload, schema=AUDIT_LOG_SCHEMA)
        print("Validation passed")
        return True, ""
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False, str(e.message)
    except Exception as e:
        print(f"Unexpected validation error: {str(e)}")
        return False, str(e)


def send_to_cloudwatch(message: str, payload: Dict[str, Any] = None):
    """Queue log message for CloudWatch (async).
    
    Args:
        message: Log message to send
        payload: Optional payload data to include
    """
    if not cloudwatch_client:
        print("CloudWatch client not available, skipping log")
        return
    
    # Add to queue for async processing
    log_queue.put((message, payload))
    print(f"Queued event for CloudWatch (queue size: {log_queue.qsize()})")


class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for webhook endpoints."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/up':
            if error_flag:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'status': 'error',
                    'message': 'Audit log webhook server is experiencing issues, please examine logs'
                }
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'status': 'ok',
                    'message': 'Audit log webhook server is running'
                }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, 'Not Found')
    
    def do_POST(self):
        """Handle POST requests (webhook payloads)."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            # Parse JSON payload
            payload = json.loads(post_data.decode('utf-8'))
            
            # Validate payload against schema
            is_valid, error_message = validate_audit_log(payload)
            if not is_valid:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'status': 'error',
                    'message': 'Invalid audit log format',
                    'detail': error_message
                }
                self.wfile.write(json.dumps(response).encode())
                print(f"Validation failed: {error_message}")
                return
            
            # Process the webhook payload
            self.process_webhook(payload)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'success',
                'message': 'Webhook received and processed'
            }
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError as e:
            self.send_error(400, f'Invalid JSON: {str(e)}')
        except Exception as e:
            self.send_error(500, f'Server error: {str(e)}')
    
    def process_webhook(self, payload: Dict[str, Any]):
        """Process the incoming webhook payload.
        
        Args:
            payload: The parsed JSON payload from the webhook
        """
        print(f"Received webhook payload: {json.dumps(payload, indent=2)}")
        
        # Send to CloudWatch Logs (async)
        send_to_cloudwatch("Webhook received", payload)
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Main entry point for the application."""
    global worker_thread
    
    # Setup CloudWatch log group
    setup_cloudwatch_log_group()
    
    # Start CloudWatch worker thread
    if cloudwatch_client:
        worker_thread = threading.Thread(target=cloudwatch_worker, daemon=False)
        worker_thread.start()
        print("CloudWatch async worker thread started")
    
    host = '0.0.0.0'
    port = 8080
    
    server = HTTPServer((host, port), WebhookHandler)
    
    print(f"Starting audit log webhook server on {host}:{port}")
    print(f"Listening for incoming webhooks at http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        shutdown_event.set()
        server.shutdown()
        
        # Wait for queue to empty
        if worker_thread:
            print("Flushing CloudWatch logs...")
            log_queue.join()
            worker_thread.join(timeout=5)
        
        print("Server stopped.")


if __name__ == "__main__":
    main()
