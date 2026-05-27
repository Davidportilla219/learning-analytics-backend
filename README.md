# Learning Analytics Platform

A production-oriented MVP of a distributed Learning Analytics platform for higher education institutions.

## Architecture

The platform consists of microservices with event-driven communication:

```
LMS/Event Source
        ↓
Event Capture Service (Port 8002)
        ↓
RabbitMQ (raw-events)
        ↓
Telemetry Processor Service (Port 8003)
        ↓
RabbitMQ (processed-events)
        ↓
Academic Risk Service (Port 8004)
        ↓
RabbitMQ (risk-alerts)
        ↓
Alert Service (Port 8005)
```

## Services

1. **API Gateway** (Port 8080) - Nginx reverse proxy and routing
2. **Auth Service** (Port 8000) - JWT-based authentication
3. **Event Capture Service** (Port 8002) - Receive and validate educational events
4. **Telemetry Processor Service** (Port 8003) - Process and normalize events
5. **Academic Risk Service** (Port 8004) - Predict academic risk using heuristics
6. **Alert Service** (Port 8005) - Generate notifications based on risk events

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for development)

### Running the Platform

```bash
# Clone the repository
git clone <repository-url>
cd learning-analytics-platform

# Start all services
docker compose up --build

# Access the services
# API Gateway: http://localhost:8080
# API Documentation: http://localhost:8080/docs
```

### Health Checks

Each service exposes health endpoints:
- `GET /health` - Service health status
- `GET /api/v1/health` - API health status
- `GET /api/v1/health/full` - Complete health check with dependencies

## API Documentation

Each service provides OpenAPI/Swagger documentation:
- API Gateway: http://localhost:8080/docs
- Auth Service: http://localhost:8080/auth/docs
- Event Capture Service: http://localhost:8080/event-capture/docs
- Telemetry Processor Service: http://localhost:8080/telemetry-processor/docs
- Academic Risk Service: http://localhost:8080/academic-risk/docs
- Alert Service: http://localhost:8080/alert/docs

### 1. Auth Service (Port 8000)

JWT-based authentication service for user management.

#### Endpoints

**Authentication**
- `POST /api/v1/users/login` - User login
- `POST /api/v1/users/register` - User registration
- `POST /api/v1/token/validate` - JWT token validation

**Health Checks**
- `GET /api/v1/health` - Service health
- `GET /api/v1/health/database` - Database health
- `GET /api/v1/health/full` - Complete health check

#### API Examples

```bash
# User login
curl -X POST "http://localhost:8080/auth/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass"
  }'

# User registration
curl -X POST "http://localhost:8080/auth/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "password123",
    "email": "user@example.com"
  }'

# Token validation
curl -X POST "http://localhost:8080/auth/api/v1/token/validate" \
  -H "Content-Type: application/json" \
  -d '{"token": "your-jwt-token"}'
```

### 2. Event Capture Service (Port 8002)

Receives and validates educational events from various learning platforms.

#### Endpoints

**Health Checks**
- `GET /api/v1/health` - Service health
- `GET /api/v1/health/database` - Database health
- `GET /api/v1/health/full` - Complete health check

**Event Management**
- `POST /api/v1/events` - Create single event
- `POST /api/v1/events/batch` - Create multiple events
- `GET /api/v1/events/{event_id}` - Get specific event
- `GET /api/v1/events` - Get events with filters
- `GET /api/v1/events/stats` - Get event statistics

#### API Examples

```bash
# Create single event
curl -X POST "http://localhost:8080/event-capture/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "event-001",
    "event_type": "login",
    "user_id": "user-001",
    "timestamp": "2026-05-27T15:00:00",
    "data": {"ip_address": "192.168.1.1"},
    "event_metadata": {"device": "desktop"}
  }'

# Create batch events
curl -X POST "http://localhost:8080/event-capture/api/v1/events/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "event_id": "event-002",
        "event_type": "page_view",
        "user_id": "user-001",
        "timestamp": "2026-05-27T15:05:00",
        "data": {"page": "/dashboard"}
      },
      {
        "event_id": "event-003",
        "event_type": "assignment_submit",
        "user_id": "user-001",
        "timestamp": "2026-05-27T15:10:00",
        "data": {"assignment_id": "assign-001", "score": 85}
      }
    ]
  }'

# Get events with filters
curl -X GET "http://localhost:8080/event-capture/api/v1/events?user_id=user-001&start_date=2026-05-27&limit=10"

# Get event statistics
curl -X GET "http://localhost:8080/event-capture/api/v1/events/stats"
```

### 3. Telemetry Processor Service (Port 8003)

Processes and normalizes raw events into structured data.

#### Endpoints

**Health Checks**
- `GET /api/v1/health` - Service health
- `GET /api/v1/health/database` - Database health
- `GET /api/v1/health/full` - Complete health check

**Event Processing**
- `POST /api/v1/events/process` - Process single event
- `GET /api/v1/events` - Get processed events
- `GET /api/v1/events/stats` - Get processing statistics

#### API Examples

```bash
# Process event
curl -X POST "http://localhost:8080/telemetry-processor/api/v1/events/process" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "processed-event-001",
    "event_type": "login",
    "user_id": "user-001",
    "timestamp": "2026-05-27T15:00:00",
    "data": {"ip_address": "192.168.1.1"},
    "event_metadata": {"device": "desktop"}
  }'

# Get processed events
curl -X GET "http://localhost:8080/telemetry-processor/api/v1/events"

# Get processing statistics
curl -X GET "http://localhost:8080/telemetry-processor/api/v1/events/stats"
```

### 4. Academic Risk Service (Port 8004)

Predicts academic risk using heuristics and machine learning models.

#### Endpoints

**Health Checks**
- `GET /api/v1/health` - Service health
- `GET /api/v1/health/database` - Database health
- `GET /api/v1/health/full` - Complete health check

**Risk Assessment**
- `POST /api/v1/risk/assess?user_id={user_id}` - Assess user risk
- `GET /api/v1/risk/profile/{user_id}` - Get user risk profile
- `GET /api/v1/risk/users` - Get users at risk
- `GET /api/v1/risk/alerts` - Get risk alerts
- `GET /api/v1/risk/stats` - Get risk statistics

**Alert Management**
- `POST /api/v1/risk/alerts/{alert_id}/acknowledge` - Acknowledge alert
- `POST /api/v1/risk/alerts/{alert_id}/resolve` - Resolve alert

#### API Examples

```bash
# Assess user risk
curl -X POST "http://localhost:8080/academic-risk/api/v1/risk/assess?user_id=user-001"

# Get user risk profile
curl -X GET "http://localhost:8080/academic-risk/api/v1/risk/profile/user-001"

# Get users at risk
curl -X GET "http://localhost:8080/academic-risk/api/v1/risk/users?risk_level=high&limit=10"

# Get risk alerts
curl -X GET "http://localhost:8080/academic-risk/api/v1/risk/alerts?user_id=user-001"

# Acknowledge alert
curl -X POST "http://localhost:8080/academic-risk/api/v1/risk/alerts/alert-001/acknowledge"

# Get risk statistics
curl -X GET "http://localhost:8080/academic-risk/api/v1/risk/stats"
```

### 5. Alert Service (Port 8005)

Generates notifications based on risk events and academic performance.

#### Endpoints

**Health Checks**
- `GET /api/v1/health` - Service health
- `GET /api/v1/health/database` - Database health
- `GET /api/v1/health/full` - Complete health check

**Alert Management**
- `POST /api/v1/alerts` - Create alert
- `GET /api/v1/alerts` - Get alerts with filters
- `GET /api/v1/alerts/{alert_id}` - Get specific alert
- `POST /api/v1/alerts/{alert_id}/acknowledge` - Acknowledge alert
- `POST /api/v1/alerts/{alert_id}/resolve` - Resolve alert
- `GET /api/v1/alerts/stats` - Get alert statistics

#### API Examples

```bash
# Create alert
curl -X POST "http://localhost:8080/alert/api/v1/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": "alert-001",
    "user_id": "user-001",
    "risk_score": 0.75,
    "risk_level": "high",
    "alert_type": "academic_risk",
    "message": "Student at high risk",
    "timestamp": "2026-05-27T15:00:00"
  }'

# Get alerts
curl -X GET "http://localhost:8080/alert/api/v1/alerts?user_id=user-001&risk_level=high"

# Get specific alert
curl -X GET "http://localhost:8080/alert/api/v1/alerts/alert-001"

# Acknowledge alert
curl -X POST "http://localhost:8080/alert/api/v1/alerts/alert-001/acknowledge"

# Resolve alert
curl -X POST "http://localhost:8080/alert/api/v1/alerts/alert-001/resolve"

# Get alert statistics
curl -X GET "http://localhost:8080/alert/api/v1/alerts/stats"
```

## Event Types Supported

### Authentication Events
- `login` - User login attempt
- `logout` - User logout

### Content Interaction Events
- `page_view` - Page viewed
- `video_play` - Video started playing
- `video_pause` - Video paused
- `video_complete` - Video completed
- `resource_download` - Resource downloaded

### Assignment Events
- `assignment_view` - Assignment viewed
- `assignment_submit` - Assignment submitted
- `assignment_grade` - Assignment graded

### Quiz Events
- `quiz_start` - Quiz started
- `quiz_submit` - Quiz submitted
- `quiz_grade` - Quiz graded

### Forum Events
- `forum_post` - Forum post created
- `forum_reply` - Forum reply created
- `forum_view` - Forum thread viewed

### Navigation Events
- `search` - Search performed
- `navigation` - Page navigation
- `assessment` - Assessment taken
- `completion` - Course completed

- **Authentication**: `login`, `logout`
- **Content Interaction**: `page_view`, `video_play`, `video_pause`, `resource_download`
- **Assignments**: `assignment_view`, `assignment_submit`
- **Quizzes**: `quiz_start`, `quiz_submit`
- **Forum**: `forum_post`, `forum_reply`
- **Navigation**: `search`, `navigation`, `assessment`, `completion`

#### API Endpoints

**Health Checks**
- `GET /api/v1/health` - Service health status
- `GET /api/v1/health/database` - Database health check
- `GET /api/v1/health/rabbitmq` - RabbitMQ health check
- `GET /api/v1/health/full` - Complete health check

**Event Management**
- `POST /api/v1/events` - Create single event
- `POST /api/v1/events/batch` - Create multiple events
- `GET /api/v1/events/{event_id}` - Get specific event
- `GET /api/v1/events` - Get events with filters (pagination, date range, user, course)
- `GET /api/v1/events/stats` - Get event statistics
- `DELETE /api/v1/events/{event_id}` - Delete event
- `GET /api/v1/events/health` - Events service health check

#### Event Schema

```json
{
  "event_id": "string (required)",
  "event_type": "string (required, enum: login, logout, page_view, etc.)",
  "user_id": "string (required)",
  "session_id": "string (optional)",
  "course_id": "string (optional)",
  "timestamp": "string (ISO 8601 format)",
  "data": "object (required, max 1MB)",
  "event_metadata": "object (optional)"
}
```

#### Running the Event Service

```bash
# Start the Event Service
docker compose up event-service

# Run tests
docker compose exec event-service python -m pytest tests/

# Run validation script
docker compose exec event-service bash test-event-service.sh

# View logs
docker compose logs -f event-service
```

#### Testing the Event Service

```bash
# Install dependencies
pip install -r event-service/requirements.txt

# Run validation script
cd event-service && ./test-event-service.sh

# Run specific tests
pytest tests/test_events.py -v
pytest tests/test_models.py -v
pytest tests/test_processor.py -v
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for development)

### Running the Platform

```bash
# Clone the repository
git clone <repository-url>
cd learning-analytics-platform

# Start all services
docker compose up --build

# Access the services
# API Gateway: http://localhost:8080
# API Documentation: http://localhost:8080/docs
```

## Development

### Running Individual Services

```bash
# Start a specific service
docker compose up auth-service
docker compose up event-service

# Run tests
docker compose exec auth-service python -m pytest tests/
docker compose exec event-service python -m pytest tests/

# View logs
docker compose logs -f auth-service
docker compose logs -f event-service
```

### Event Service Development

```bash
# Navigate to event service directory
cd event-service

# Install dependencies
pip install -r requirements.txt

# Run validation script
./test-event-service.sh

# Run specific test categories
pytest tests/test_events.py -v          # API endpoint tests
pytest tests/test_models.py -v          # Model validation tests
pytest tests/test_processor.py -v       # Event processor tests

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres

# RabbitMQ configuration
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# JWT configuration
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Event Service configuration
SERVICE_NAME=event-capture-service
PORT=8002
LOG_LEVEL=INFO
MAX_EVENT_SIZE=1048576
BATCH_SIZE=100
PROCESSING_TIMEOUT=30

# CORS configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS=["*"]
```

## API Documentation

Each service provides OpenAPI/Swagger documentation:
- API Gateway: http://localhost:8080/docs
- Auth Service: http://localhost:8080/auth/docs
- Event Capture Service: http://localhost:8080/event-capture/docs
- Telemetry Processor Service: http://localhost:8080/telemetry-processor/docs
- Academic Risk Service: http://localhost:8080/academic-risk/docs
- Alert Service: http://localhost:8080/alert/docs

### Event Capture Service API Examples

**Create a single event:**
```bash
curl -X POST "http://localhost:8080/event-capture/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "event-001",
    "event_type": "login",
    "user_id": "user-001",
    "timestamp": "2024-01-01T10:00:00Z",
    "data": {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"},
    "event_metadata": {"device": "desktop", "browser": "chrome"}
  }'
```

**Create multiple events:**
```bash
curl -X POST "http://localhost:8080/event-capture/api/v1/events/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "event_id": "event-002",
        "event_type": "page_view",
        "user_id": "user-001",
        "session_id": "session-001",
        "course_id": "course-001",
        "timestamp": "2024-01-01T10:05:00Z",
        "data": {"page": "/dashboard", "duration": 30}
      },
      {
        "event_id": "event-003",
        "event_type": "assignment_view",
        "user_id": "user-001",
        "session_id": "session-001",
        "course_id": "course-001",
        "timestamp": "2024-01-01T10:10:00Z",
        "data": {"assignment_id": "assignment-001", "title": "Math Assignment"}
      }
    ]
  }'
```

**Get events with filters:**
```bash
curl -X GET "http://localhost:8080/event-capture/api/v1/events?user_id=user-001&start_date=2024-01-01&end_date=2024-01-02&page=1&limit=10"
```

**Get event statistics:**
```bash
curl -X GET "http://localhost:8080/event-capture/api/v1/events/stats"
```

**Check service health:**
```bash
curl -X GET "http://localhost:8080/event-capture/api/v1/health/full"
```

## Testing

### Running Tests

```bash
# Run comprehensive test suite
./test-all-services.sh

# Run individual service tests
docker compose exec auth-service python -m pytest tests/
docker compose exec event-service python -m pytest tests/
docker compose exec telemetry-processor-service python -m pytest tests/
docker compose exec academic-risk-service python -m pytest tests/
docker compose exec alert-service python -m pytest tests/

# Run specific test files
docker compose exec auth-service python -m pytest tests/test_auth.py
docker compose exec event-service python -m pytest tests/test_events.py
docker compose exec event-service python -m pytest tests/test_models.py
docker compose exec event-service python -m pytest tests/test_processor.py

# Run validation scripts
docker compose exec event-service bash test-event-service.sh
```

### Test Categories

- **Health Checks**: Verify all services are running and healthy
- **API Endpoints**: Test all REST API endpoints
- **Error Handling**: Test invalid requests and error responses
- **Performance**: Test concurrent requests and bulk operations
- **Database Integration**: Test data persistence and retrieval
- **Cross-Service Communication**: Test inter-service communication

## Deployment

### Production Deployment

1. **Prerequisites**
   - Docker and Docker Compose installed
   - Sufficient server resources (minimum 4GB RAM, 2 CPU cores)
   - Port availability (8080, 8000-8005, 5432, 5672)

2. **Environment Configuration**
   ```bash
   # Copy and modify environment file
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Start Services**
   ```bash
   # Build and start all services
   docker compose up -d

   # Check service status
   docker compose ps

   # View logs
   docker compose logs -f
   ```

4. **Health Monitoring**
   ```bash
   # Check all service health
   curl http://localhost:8080/health

   # Check individual services
   curl http://localhost:8080/auth/api/v1/health
   curl http://localhost:8080/event-capture/api/v1/health
   curl http://localhost:8080/telemetry-processor/api/v1/health
   curl http://localhost:8080/academic-risk/api/v1/health
   curl http://localhost:8080/alert/api/v1/health
   ```

### Scaling and Monitoring

```bash
# Scale services horizontally
docker compose up --scale auth-service=3 -d

# Monitor resource usage
docker stats

# Check container logs
docker compose logs -f auth-service

# Health check monitoring
watch -n 30 "curl -s http://localhost:8080/health | jq ."
```

### Database Management

```bash
# Access PostgreSQL database
docker compose exec postgres psql -U postgres -d learning_analytics

# Backup database
docker compose exec postgres pg_dump -U postgres learning_analytics > backup.sql

# Restore database
docker compose exec -T postgres psql -U postgres learning_analytics < backup.sql
```

### Maintenance

```bash
# Stop all services
docker compose down

# Remove containers and volumes
docker compose down -v

# Clean up unused images
docker image prune

# Update services
docker compose pull
docker compose up -d
```

## Development Workflow

1. **Setup Development Environment**
   ```bash
   git clone <repository-url>
   cd learning-analytics-platform
   docker compose up -d
   ```

2. **Development Process**
   - Create feature branch
   - Write tests for new functionality
   - Implement service changes
   - Run comprehensive test suite
   - Test API endpoints manually
   - Submit pull request

3. **Code Quality**
   - Follow existing code patterns
   - Maintain consistent logging levels
   - Use proper error handling
   - Document new endpoints
   - Keep dependencies updated

## Monitoring and Observability

### Health Checks

Each service exposes multiple health endpoints:
- `GET /health` - Basic service health
- `GET /api/v1/health` - API health status
- `GET /api/v1/health/full` - Complete health check with dependencies
- `GET /api/v1/health/database` - Database connection health
- `GET /api/v1/health/rabbitmq` - Message broker health

### Logging

Services use structured logging with configurable levels:
- `DEBUG` - Detailed debugging information
- `INFO` - General operational information
- `WARNING` - Warning conditions
- `ERROR` - Error conditions
- `CRITICAL` - Critical conditions

### Metrics

Key metrics to monitor:
- Request rates and response times
- Database query performance
- RabbitMQ queue sizes and message rates
- Error rates and status codes
- Resource utilization (CPU, memory, disk)

## Contributing

Please follow the development plan and ensure all tests pass before submitting changes.

### Code Style Guidelines

- Follow existing code patterns and structure
- Use meaningful variable and function names
- Implement proper error handling
- Add appropriate logging
- Document new features and endpoints
- Keep dependencies updated and secure

### Testing Requirements

- All new features must include comprehensive tests
- Test coverage should be maintained above 80%
- Integration tests must pass for all services
- Performance tests should be run for major changes
- Manual testing of API endpoints is required