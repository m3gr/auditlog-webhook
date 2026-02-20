# Audit Log Webhook

[![Build Docker Image](https://github.com/m3gr/auditlog-webhook/actions/workflows/docker-build.yml/badge.svg)](https://github.com/m3gr/auditlog-webhook/actions/workflows/docker-build.yml)

A Python project for handling audit log webhooks using AWS services.

## API Documentation

The API follows the OpenAPI 3.0 specification. See [openapi.yaml](openapi.yaml) for the complete API documentation.

### Audit Log Event Schema

```json
{
  "date": "2026-02-17 14:30:45.123 -0500",
  "application": "mrbeta.m3globalresearch.com",
  "ipaddr": "192.168.123.234",
  "userid": "userabc123",
  "result": true,
  "eventtype": "login",
  "message": {
    "detail": "User attempted password reset"
  }
}
```

**Field Descriptions:**
- `date` (string): ISO8601 date - `YYYY-MM-DD HH:mm:ss.sss ZZZZ`
- `application` (string): Application FQDN
- `ipaddr` (string): IP Address
- `userid` (string): User ID
- `result` (boolean): True for success, False for failure
- `eventtype` (string): Event type (`login`, `password_change`, `acl_change`)
- `message` (object): JSON object with event details

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure AWS credentials:
   ```bash
   # Option 1: Using AWS CLI
   aws configure
   
   # Option 2: Set environment variables
   set AWS_ACCESS_KEY_ID=your_access_key
   set AWS_SECRET_ACCESS_KEY=your_secret_key
   set AWS_SESSION_TOKEN=your_session_token
   set AWS_DEFAULT_REGION=us-east-1
   ```

## Features

- HTTP webhook listener on port 8080
- Automatic CloudWatch Logs integration
- JSON payload validation
- Error handling and logging
\
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
```

### View API Documentation:

You can visualize the OpenAPI specification using:
- [Swagger Editor](https://editor.swagger.io/) - paste the contents of [openapi.yaml](openapi.yaml)
- [Swagger UI](https://petstore.swagger.io/) - use the "Explore" feature with the openapi.yaml URLCloudWatch Configuration

The application automatically creates and uses the following AWS resources:
- **Log Group**: `appl_audit_log`
- **Log Stream**: `webhook-YYYY-MM-DD` (daily rotation)

All incoming webhook payloads are logged to CloudWatch for audit purposes.

## Dependencies

- **boto3**: AWS SDK for Python
- **requests**: HTTP library for making API requests

## Usage

```bash
python src\main.py
```

The server will start on `http://localhost:8080`

### Test the webhook:

```bash
# Check server status
curl http://localhost:8080

# Send a webhook POST request
curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d "{\"event\":\"test\",\"data\":\"sample\"}"
```

## Docker Deployment

### Build and run with Docker:

```bash
# Build the image
docker build -t audit-log-webhook .

# Run the container
docker run -d -p 8080:8080 \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  -e AWS_DEFAULT_REGION=us-east-1 \
  --name audit-log-webhook \
  audit-log-webhook
```

### Using Docker Compose:

```bash
# Set AWS credentials in environment
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token
export AWS_DEFAULT_REGION=us-east-1

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f


## GitHub Actions CI/CD

The project includes automated workflows:

### Docker Build Workflow
- **Triggers**: Push to main/develop, tags, pull requests
- **Actions**:
  - Builds Docker image with Buildx
  - Pushes to GitHub Container Registry (ghcr.io)
  - Tags images based on git refs (branch, tag, SHA)
  - Runs Trivy security scanner
  - Uploads vulnerability reports to GitHub Security

**Pull the image from GitHub Container Registry:**
```bash
docker pull ghcr.io/m3gr/auditlog-webhook:latest
```

# Stop the service
docker-compose down
```
