# Learning Analytics Platform - Deployment Guide

## Production Deployment

This guide provides step-by-step instructions for deploying the Learning Analytics Platform in a production environment.

## Prerequisites

### System Requirements
- **CPU**: Minimum 2 cores, recommended 4+ cores
- **Memory**: Minimum 4GB RAM, recommended 8GB+ RAM
- **Storage**: Minimum 20GB free space, SSD recommended
- **Network**: Stable internet connection with adequate bandwidth

### Software Requirements
- Docker (version 20.10+)
- Docker Compose (version 1.29+)
- Git (for repository management)

### Port Requirements
| Port | Service | Protocol | Description |
|------|---------|----------|-------------|
| 8080 | API Gateway | HTTP | Main entry point |
| 8000 | Auth Service | HTTP | Authentication service |
| 8002 | Event Capture | HTTP | Event ingestion |
| 8003 | Telemetry Processor | HTTP | Event processing |
| 8004 | Academic Risk | HTTP | Risk assessment |
| 8005 | Alert Service | HTTP | Alert management |
| 5432 | PostgreSQL | TCP | Database |
| 5672 | RabbitMQ | TCP | Message broker |
| 15672 | RabbitMQ Management | HTTP | Management UI |

## Deployment Steps

### 1. Prepare the Server

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in to apply group changes
```

### 2. Clone and Setup Repository

```bash
# Clone the repository
git clone <repository-url>
cd learning-analytics-platform

# Create production environment file
cp .env.example .env

# Edit the environment file with production values
nano .env
```

### 3. Configure Environment Variables

Edit `.env` file with production values:

```bash
# Service Configuration
SERVICE_NAME=learning-analytics-platform
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-secure-password-here
DB_NAME=learning_analytics

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=your-secure-password-here

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Service Ports
AUTH_PORT=8000
EVENT_PORT=8002
TELEMETRY_PORT=8003
RISK_PORT=8004
ALERT_PORT=8005
GATEWAY_PORT=8080

# CORS Configuration
CORS_ORIGINS=["https://your-domain.com", "https://app.your-domain.com"]
CORS_ALLOW_CREDENTIALS=true

# Security Configuration
MAX_EVENT_SIZE=1048576
BATCH_SIZE=100
PROCESSING_TIMEOUT=30
ALERT_RETENTION_DAYS=30
```

### 4. Build and Deploy Services

```bash
# Build all services
docker compose build

# Start all services in detached mode
docker compose up -d

# Check service status
docker compose ps

# View initial logs
docker compose logs -f
```

### 5. Verify Deployment

```bash
# Check overall health
curl http://localhost:8080/health

# Check individual services
curl http://localhost:8080/auth/api/v1/health
curl http://localhost:8080/event-capture/api/v1/health
curl http://localhost:8080/telemetry-processor/api/v1/health
curl http://localhost:8080/academic-risk/api/v1/health
curl http://localhost:8080/alert/api/v1/health

# Run comprehensive test suite
./test-all-services.sh
```

### 6. Configure Reverse Proxy (Optional)

For production, configure Nginx as a reverse proxy:

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/learning-analytics
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # API Gateway
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support for real-time features
    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Static files
    location /static {
        alias /var/www/learning-analytics/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/learning-analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Configure SSL/TLS (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Monitoring and Maintenance

### Health Monitoring

```bash
# Create health monitoring script
cat > health-check.sh << 'EOF'
#!/bin/bash

# Health check script
BASE_URL="http://localhost:8080"

services=("auth" "event-capture" "telemetry-processor" "academic-risk" "alert")

for service in "${services[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/$service/api/v1/health")
    if [ "$response" -eq 200 ]; then
        echo "✓ $service: OK"
    else
        echo "✗ $service: FAILED ($response)"
    fi
done
EOF

chmod +x health-check.sh

# Set up cron job for health monitoring
echo "*/5 * * * * $(pwd)/health-check.sh" | crontab -
```

### Log Management

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/learning-analytics

# Add configuration:
/var/log/learning-analytics/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

### Database Maintenance

```bash
# Create backup script
cat > backup-database.sh << 'EOF'
#!/bin/bash

# Database backup script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/learning-analytics"
DB_NAME="learning_analytics"

mkdir -p $BACKUP_DIR

# Create backup
docker compose exec postgres pg_dump -U postgres $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_DIR/backup_$DATE.sql.gz"
EOF

chmod +x backup-database.sh

# Set up daily backup
echo "0 2 * * * $(pwd)/backup-database.sh" | crontab -
```

### Performance Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor resource usage
htop
docker stats

# Monitor disk usage
df -h
du -sh /var/lib/docker
```

## Scaling and Optimization

### Horizontal Scaling

```bash
# Scale services based on load
docker compose up --scale event-capture=3 -d
docker compose up --scale telemetry-processor=2 -d
docker compose up --scale academic-risk=2 -d

# Scale back when load decreases
docker compose up --scale event-capture=1 -d
```

### Database Optimization

```bash
# Monitor database performance
docker compose exec postgres psql -U postgres -d learning_analytics -c "SELECT * FROM pg_stat_activity;"

# Optimize database
docker compose exec postgres psql -U postgres -d learning_analytics -c "VACUUM ANALYZE;"

# Create indexes for better performance
docker compose exec postgres psql -U postgres -d learning_analytics -c "
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
"
```

### RabbitMQ Optimization

```bash
# Monitor RabbitMQ queues
curl -u guest:guest http://localhost:15672/api/queues

# Clean up unused queues
docker compose exec rabbitmq rabbitmqctl list_queues

# Set message TTL
docker compose exec rabbitmq rabbitmqctl set_policy TTL ".*" '{"message-ttl":86400000}' --apply-to queues
```

## Troubleshooting

### Common Issues

1. **Services Not Starting**
   ```bash
   # Check logs
   docker compose logs -f [service-name]
   
   # Check resource usage
   docker stats
   
   # Restart services
   docker compose restart [service-name]
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   docker compose exec postgres psql -U postgres -d learning_analytics -c "SELECT version();"
   
   # Check database logs
   docker compose logs postgres
   ```

3. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   sudo nano /etc/docker/daemon.json
   
   # Add:
   {
     "memory": "8192m"
   }
   
   # Restart Docker
   sudo systemctl restart docker
   ```

### Performance Issues

1. **Slow API Responses**
   - Check database indexes
   - Monitor RabbitMQ queue sizes
   - Increase service instances

2. **High Memory Usage**
   - Monitor service memory usage
   - Check for memory leaks
   - Adjust Docker memory limits

3. **Database Performance**
   - Monitor slow queries
   - Optimize indexes
   - Consider database scaling

### Security Considerations

1. **Change Default Passwords**
   ```bash
   # Change PostgreSQL password
   docker compose exec postgres psql -U postgres -c "ALTER USER postgres PASSWORD 'new-secure-password';"
   ```

2. **Network Security**
   ```bash
   # Configure firewall
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny 8000-8005/tcp
   sudo ufw enable
   ```

3. **SSL/TLS Configuration**
   - Use Let's Encrypt certificates
   - Configure HTTPS redirect
   - Implement certificate auto-renewal

## Backup and Recovery

### Backup Strategy

1. **Daily Database Backups**
2. **Weekly Application Backups**
3. **Monthly Configuration Backups**

### Recovery Procedure

1. **Stop Services**
   ```bash
   docker compose down
   ```

2. **Restore Database**
   ```bash
   docker compose exec -T postgres psql -U postgres learning_analytics < backup.sql
   ```

3. **Start Services**
   ```bash
   docker compose up -d
   ```

### Disaster Recovery

1. **Automated Backup Script**
2. **Off-site Backup Storage**
3. **Regular Recovery Testing**

## Support and Maintenance

### Support Channels

- **Documentation**: [Link to documentation]
- **Issue Tracker**: [Link to GitHub issues]
- **Email**: support@your-domain.com

### Maintenance Schedule

- **Daily**: Health checks and log review
- **Weekly**: Performance monitoring and optimization
- **Monthly**: Security updates and backups
- **Quarterly**: System upgrades and major updates

### Contact Information

- **Technical Support**: support@your-domain.com
- **System Administrator**: admin@your-domain.com
- **Development Team**: dev@your-domain.com

---

This deployment guide provides comprehensive instructions for deploying and maintaining the Learning Analytics Platform in a production environment. Always test changes in a staging environment before deploying to production.