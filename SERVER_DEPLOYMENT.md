# Learning Analytics Platform - Server Deployment Guide

## 1) Prerequisites
- Ubuntu 22.04+ (or compatible Linux)
- Docker Engine 24+
- Docker Compose plugin 2+
- Ports open: `8080`, `5433`, `5672`, `15672`

## 2) Clone and enter project
```bash
git clone <your-repo-url>
cd microservices-design/learning-analytics-platform
```

## 3) Environment review
Ensure these values are correct in `docker-compose.yml` (already wired by default):
- Postgres user/password: `postgres/postgres`
- Auth DB: `auth_service_db`
- Event DB: `event_service_db`

## 4) Important: first boot DB initialization
Postgres init scripts run only on first empty volume creation.

If this is a fresh server:
```bash
docker compose up -d
```

If you already ran old volumes and need DB recreation:
```bash
docker compose down -v
docker compose up -d
```

## 5) Build/start commands
```bash
docker compose build
docker compose up -d
docker compose ps -a
```

## 6) Health verification (must pass)
```bash
curl -sS http://127.0.0.1:8080/health
curl -sS http://127.0.0.1:8080/auth/api/v1/health
curl -sS http://127.0.0.1:8080/event-capture/api/v1/health
```

Expected:
- Gateway returns `{"status":"ok","service":"gateway"}`
- Auth health returns `service":"auth-service"`
- Event health returns `service":"Event Capture Service"`

## 7) Business endpoint smoke tests
Register:
```bash
curl -sS -X POST http://127.0.0.1:8080/auth/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"server_user_1","email":"server_user_1@example.com","password":"SecurePass123!","first_name":"Server","last_name":"User"}'
```

Login:
```bash
curl -sS -X POST http://127.0.0.1:8080/auth/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"server_user_1","password":"SecurePass123!"}'
```

## 8) Logs and troubleshooting
```bash
docker compose logs --tail=200 auth-service
docker compose logs --tail=200 event-service
docker compose logs --tail=200 gateway
```

If auth/event returns DB errors:
- Recreate volumes so init SQL executes:
```bash
docker compose down -v
docker compose up -d
```

## 9) Operational commands
Restart all:
```bash
docker compose restart
```

Stop all:
```bash
docker compose down
```

Stop + remove data:
```bash
docker compose down -v
```
