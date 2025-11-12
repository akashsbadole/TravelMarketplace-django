# Travel Marketplace - Deployment Guide

This guide covers the complete deployment process for the Travel Marketplace application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Application Configuration](#application-configuration)
5. [Deployment Methods](#deployment-methods)
6. [Testing](#testing)
7. [Monitoring](#monitoring)
8. [Security](#security)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04+ or CentOS 8+
- **Python**: 3.9+
- **Node.js**: 16+ (for frontend build tools)
- **PostgreSQL**: 12+
- **Redis**: 6+
- **Nginx**: 1.18+
- **SSL Certificate**: For production HTTPS

### Software Dependencies

```bash
# System packages
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3-pip nodejs npm postgresql-12 redis-server nginx certbot

# Python packages
pip install django==4.2.* gunicorn celery redis psycopg2-binary pillow

# Node packages (if building frontend)
npm install -g @vue/cli @vue/compiler-sfc
```

### Hardware Requirements

- **Minimum**: 2 CPU cores, 4GB RAM, 20GB storage
- **Recommended**: 4 CPU cores, 8GB RAM, 50GB storage
- **Database**: Separate SSD storage recommended for PostgreSQL

## Environment Setup

### 1. Create Project Directory

```bash
sudo mkdir -p /opt/travel_marketplace
sudo chown $USER:$USER /opt/travel_marketplace
cd /opt/travel_marketplace
```

### 2. Clone Repository

```bash
git clone https://github.com/your-org/travel-marketplace.git .
git checkout production  # or your production branch
```

### 3. Python Environment

```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Environment Variables

Copy the example environment file and configure:

```bash
cp deploy/.env.example .env
nano .env
```

Required variables:
- `SECRET_KEY`: Django secret key (generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ALLOWED_HOSTS`: Comma-separated list of allowed domains

## Database Configuration

### 1. PostgreSQL Setup

```bash
# Create database user
sudo -u postgres createuser --interactive travel_marketplace

# Create database
sudo -u postgres createdb -O travel_marketplace travel_marketplace

# Set password
sudo -u postgres psql -c "ALTER USER travel_marketplace PASSWORD 'your_secure_password';"
```

### 2. Database Configuration

Update `.env` file:

```bash
DATABASE_URL=postgresql://travel_marketplace:your_secure_password@localhost:5432/travel_marketplace
```

### 3. Run Migrations

```bash
python manage.py migrate
```

## Application Configuration

### 1. Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# Set proper permissions
sudo chown -R www-data:www-data /opt/travel_marketplace/staticfiles
sudo chown -R www-data:www-data /opt/travel_marketplace/media
```

### 2. Celery Configuration

```bash
# Create Celery user and directories
sudo useradd -r -s /bin/false celery
sudo mkdir -p /var/log/celery /var/run/celery
sudo chown -R celery:celery /var/log/celery /var/run/celery
```

### 3. SSL Certificate

```bash
# Let's Encrypt for production
sudo certbot --nginx -d travelmarketplace.com -d www.travelmarketplace.com

# Or use custom certificates
sudo cp your-cert.pem /etc/nginx/ssl/cert.pem
sudo cp your-key.pem /etc/nginx/ssl/key.pem
```

## Deployment Methods

### Method 1: Docker Deployment (Recommended)

#### 1. Build Docker Image

```bash
# Build image
docker build -t travel-marketplace:latest .

# Tag with version
docker tag travel-marketplace:latest travel-marketplace:v1.0.0
```

#### 2. Deploy with Docker Compose

```bash
# Copy environment file
cp deploy/.env.example .env

# Edit environment variables
nano .env

# Deploy
docker-compose -f deploy/docker-compose.yml up -d
```

#### 3. Docker Compose Services

- **web**: Django application with Gunicorn
- **db**: PostgreSQL database
- **redis**: Redis cache and message broker
- **celery**: Background task processing
- **celery-beat**: Scheduled task execution
- **nginx**: Reverse proxy and SSL termination

### Method 2: Manual Deployment

#### 1. Systemd Services

Create service files:

```bash
# Gunicorn service
sudo nano /etc/systemd/system/travel-marketplace.service
```

```ini
[Unit]
Description=Travel Marketplace Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/travel_marketplace
Environment=PATH=/opt/travel_marketplace/venv/bin
ExecStart=/opt/travel_marketplace/venv/bin/gunicorn travel_marketplace.wsgi:application --workers 3 --bind unix:/run/travel-marketplace.sock
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Celery worker service
sudo nano /etc/systemd/system/celery.service
```

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=celery
Group=celery
WorkingDirectory=/opt/travel_marketplace
Environment=PATH=/opt/travel_marketplace/venv/bin
ExecStart=/opt/travel_marketplace/venv/bin/celery -A travel_marketplace worker --loglevel=INFO
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

#### 2. Nginx Configuration

```bash
# Copy Nginx configuration
sudo cp deploy/nginx/nginx.conf /etc/nginx/sites-available/travel-marketplace

# Enable site
sudo ln -s /etc/nginx/sites-available/travel-marketplace /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### 3. Start Services

```bash
# Start and enable services
sudo systemctl daemon-reload
sudo systemctl enable travel-marketplace
sudo systemctl enable celery
sudo systemctl enable nginx

# Start services
sudo systemctl start travel-marketplace
sudo systemctl start celery
sudo systemctl start nginx
```

## Testing

### 1. Automated Tests

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### 2. Integration Tests

```bash
# Run integration tests
python tests/integration_tests.py

# Test specific modules
python manage.py test users.tests.UserTestCase
python manage.py test agents.tests.AgentTestCase
python manage.py test bookings.tests.BookingTestCase
```

### 3. Load Testing

```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/locustfile.py --host=https://travelmarketplace.com --users=100 --spawn-rate=10 --run-time=60
```

### 4. Security Testing

```bash
# Install security tools
pip install bandit safety
npm install -g audit-ci

# Run security scans
bandit -r travel_marketplace
safety check
audit-ci .
```

## Monitoring

### 1. Application Monitoring

#### Health Checks

```bash
# Health check endpoint
curl https://travelmarketplace.com/health/

# Detailed health
curl https://travelmarketplace.com/health/detailed/
```

#### Logging

```bash
# View application logs
tail -f /var/log/django/travel_marketplace.log

# View error logs
tail -f /var/log/django/travel_marketplace_error.log

# View Nginx logs
tail -f /var/log/nginx/travel_marketplace_access.log
```

### 2. Performance Monitoring

#### APM Setup

```python
# Add to requirements.txt
sentry-sdk
newrelic
datadog

# Configure in settings.py
SENTRY_DSN=your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your-newrelic-key
```

#### Database Monitoring

```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 100;
ALTER SYSTEM SET log_statement = 'all';

-- Monitor connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
```

### 3. Infrastructure Monitoring

#### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'travel-marketplace'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

#### Grafana Dashboard

- Request rate and response times
- Database performance
- Celery task queue length
- Error rates by endpoint
- User activity metrics

## Security

### 1. Firewall Configuration

```bash
# UFW setup
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Security Headers

The application includes security headers:
- HSTS
- X-Frame-Options
- X-Content-Type-Options
- CSP headers
- Rate limiting

### 3. SSL Configuration

```bash
# Test SSL configuration
sudo nginx -t
sudo openssl s_client -connect travelmarketplace.com:443 -servername travelmarketplace.com

# Check certificate expiry
openssl x509 -in /etc/nginx/ssl/cert.pem -noout -dates
```

### 4. Regular Security Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs pip install -U

# Security scan
bandit -r travel_marketplace
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U travel_marketplace -d travel_marketplace -h localhost

# Check logs
sudo tail -f /var/log/postgresql/postgresql-12-main.log
```

#### 2. Static Files Not Loading

```bash
# Check permissions
ls -la /opt/travel_marketplace/staticfiles/

# Check Nginx configuration
grep -n "static" /etc/nginx/sites-available/travel-marketplace

# Recollect static files
python manage.py collectstatic --noinput --clear
```

#### 3. Celery Tasks Not Processing

```bash
# Check Redis connection
redis-cli ping

# Check Celery workers
celery -A travel_marketplace inspect active

# Check queue length
celery -A travel_marketplace inspect reserved
```

#### 4. High Memory Usage

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Check Gunicorn workers
ps aux | grep gunicorn

# Restart services if needed
sudo systemctl restart travel-marketplace
```

### Performance Optimization

#### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX CONCURRENTLY idx_requirements_status ON requirements(status);
CREATE INDEX CONCURRENTLY idx_quotes_agent ON quotes(agent_id);
CREATE INDEX CONCURRENTLY idx_bookings_user ON bookings(user_id);

-- Analyze tables
ANALYZE requirements;
ANALYZE quotes;
ANALYZE bookings;
```

#### 2. Caching Configuration

```python
# Redis cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESS_MIN_LEN': 50,
            'COMPRESS_THRESHOLD': 5000,
        }
    }
}
```

#### 3. Application Tuning

```python
# Gunicorn settings
bind = "unix:/run/travel-marketplace.sock"
workers = min(2 * cpu_count() + 1, 4)
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 2
```

## Deployment Script Usage

### Automated Deployment

```bash
# Make deploy script executable
chmod +x deploy/deploy.sh

# Deploy
./deploy/deploy.sh deploy

# Rollback if needed
./deploy/deploy.sh rollback

# Check health
./deploy/deploy.sh health
```

### Backup and Recovery

```bash
# Manual backup
./deploy/deploy.sh backup

# List backups
ls -la /var/backups/

# Restore from backup
./deploy/deploy.sh rollback
```

## Maintenance

### Regular Tasks

1. **Daily**:
   - Database backups
   - Log rotation
   - SSL certificate renewal check
   - Security updates

2. **Weekly**:
   - System updates
   - Performance optimization
   - Cache cleanup

3. **Monthly**:
   - Security audits
   - Performance reviews
   - Capacity planning

### Monitoring Alerts

Set up alerts for:
- High error rates (>5%)
- High response times (>2s)
- Database connection issues
- Disk space >80%
- Memory usage >90%
- SSL certificate expiry (30 days)

## Support and Documentation

### Documentation Links

- [API Documentation](https://docs.travelmarketplace.com/api)
- [Admin Guide](https://docs.travelmarketplace.com/admin)
- [User Guide](https://docs.travelmarketplace.com/user)
- [Troubleshooting Guide](https://docs.travelmarketplace.com/troubleshoot)

### Emergency Contacts

- **Technical Support**: support@travelmarketplace.com
- **Security Issues**: security@travelmarketplace.com
- **Downtime Reporting**: status@travelmarketplace.com

### Version Information

- **Current Version**: 1.0.0
- **Release Notes**: [CHANGELOG.md](CHANGELOG.md)
- **Upgrade Guide**: [UPGRADE.md](UPGRADE.md)

---

**Note**: This deployment guide assumes a production environment. For development setup, please refer to the [Development Guide](DEVELOPMENT.md).