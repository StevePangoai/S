# Shopify AI Agent - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Shopify AI Agent application in various environments, from local development to production deployment.

## Quick Start

### Prerequisites Checklist

- [ ] Python 3.11 or higher installed
- [ ] Shopify store with Admin API access
- [ ] OpenAI API key
- [ ] Git installed (for cloning)

### 1-Minute Setup

```bash
# Clone and setup
git clone <repository-url>
cd shopify-ai-agent

# Run the startup script
./start.sh
```

The startup script will:
- Create virtual environment
- Install dependencies
- Prompt for environment variables
- Start the application

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```env
# Shopify Configuration
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SHOPIFY_STOREFRONT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MYSHOPIFY_DOMAIN=your-store.myshopify.com

# OpenAI Configuration
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_BASE=https://api.openai.com/v1

# Optional: Flask Configuration
FLASK_DEBUG=0
FLASK_ENV=production
```

### Obtaining Shopify Credentials

#### Admin API Access Token

1. **Access Shopify Admin**
   - Log into your Shopify admin panel
   - Navigate to **Apps** → **App and sales channel settings**

2. **Create Private App**
   - Click **Develop apps**
   - Click **Create an app**
   - Enter app name: "AI Agent"

3. **Configure API Scopes**
   Required scopes:
   - `read_products` - View products
   - `write_products` - Create/modify products
   - `read_orders` - View orders
   - `write_orders` - Modify orders
   - `read_customers` - View customers
   - `write_customers` - Modify customers
   - `read_inventory` - View inventory
   - `write_inventory` - Modify inventory

4. **Install and Get Token**
   - Click **Install app**
   - Copy the **Admin API access token**

#### Storefront API Token

1. In the same app configuration
2. Enable **Storefront API access**
3. Select required permissions
4. Copy the **Storefront access token**

## Local Development

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SHOPIFY_ACCESS_TOKEN="your_token"
export MYSHOPIFY_DOMAIN="your-store.myshopify.com"
export OPENAI_API_KEY="your_openai_key"

# Start development server
python src/main.py
```

### Development Features

- **Hot Reload**: Automatic restart on code changes
- **Debug Mode**: Detailed error messages
- **CORS Enabled**: Frontend-backend communication
- **SQLite Database**: Local data storage

### Testing the Application

1. **Access the Interface**
   - Open browser to `http://localhost:5000`
   - Verify the UI loads correctly

2. **Test Chat Functionality**
   - Enter: "What is my store name?"
   - Verify AI response

3. **Test Quick Actions**
   - Click "View Products"
   - Click "Store Info"
   - Verify data loads

4. **API Testing**
   ```bash
   # Test health endpoint
   curl http://localhost:5000/api/ai/health
   
   # Test store info
   curl http://localhost:5000/api/shopify/store-info
   ```

## Production Deployment

### Option 1: Traditional Server Deployment

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Create application user
sudo useradd -m -s /bin/bash shopify-agent
sudo su - shopify-agent
```

#### 2. Application Setup

```bash
# Clone repository
git clone <repository-url>
cd shopify-ai-agent

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

#### 3. Environment Configuration

```bash
# Create production environment file
cat > .env << EOF
SHOPIFY_ACCESS_TOKEN=your_production_token
MYSHOPIFY_DOMAIN=your-store.myshopify.com
OPENAI_API_KEY=your_openai_key
OPENAI_API_BASE=https://api.openai.com/v1
FLASK_ENV=production
FLASK_DEBUG=0
EOF

# Secure the environment file
chmod 600 .env
```

#### 4. Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
# Gunicorn configuration
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = "shopify-agent"
group = "shopify-agent"
tmp_upload_dir = None
errorlog = "/var/log/shopify-agent/error.log"
accesslog = "/var/log/shopify-agent/access.log"
loglevel = "info"
```

#### 5. Systemd Service

Create `/etc/systemd/system/shopify-agent.service`:

```ini
[Unit]
Description=Shopify AI Agent
After=network.target

[Service]
Type=exec
User=shopify-agent
Group=shopify-agent
WorkingDirectory=/home/shopify-agent/shopify-ai-agent
Environment=PATH=/home/shopify-agent/shopify-ai-agent/venv/bin
ExecStart=/home/shopify-agent/shopify-ai-agent/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 6. Nginx Configuration

Create `/etc/nginx/sites-available/shopify-agent`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias /home/shopify-agent/shopify-ai-agent/src/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 7. SSL Configuration (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 8. Start Services

```bash
# Create log directory
sudo mkdir -p /var/log/shopify-agent
sudo chown shopify-agent:shopify-agent /var/log/shopify-agent

# Enable and start services
sudo systemctl enable shopify-agent
sudo systemctl start shopify-agent
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status shopify-agent
sudo systemctl status nginx
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY .env .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/ai/health || exit 1

# Start application
CMD ["python", "src/main.py"]
```

#### 2. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  shopify-agent:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SHOPIFY_ACCESS_TOKEN=${SHOPIFY_ACCESS_TOKEN}
      - MYSHOPIFY_DOMAIN=${MYSHOPIFY_DOMAIN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_API_BASE=${OPENAI_API_BASE}
    volumes:
      - ./src/database:/app/src/database
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/ai/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - shopify-agent
    restart: unless-stopped
```

#### 3. Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f shopify-agent

# Scale application
docker-compose up -d --scale shopify-agent=3
```

### Option 3: Cloud Platform Deployment

#### Heroku Deployment

1. **Prepare for Heroku**
   ```bash
   # Install Heroku CLI
   curl https://cli-assets.heroku.com/install.sh | sh
   
   # Login
   heroku login
   ```

2. **Create Procfile**
   ```
   web: gunicorn src.main:app
   ```

3. **Deploy**
   ```bash
   # Create app
   heroku create your-app-name
   
   # Set environment variables
   heroku config:set SHOPIFY_ACCESS_TOKEN=your_token
   heroku config:set MYSHOPIFY_DOMAIN=your-store.myshopify.com
   heroku config:set OPENAI_API_KEY=your_openai_key
   
   # Deploy
   git push heroku main
   ```

#### AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize and Deploy**
   ```bash
   eb init
   eb create production
   eb deploy
   ```

## Monitoring and Maintenance

### Health Monitoring

#### Application Health Checks

```bash
# Basic health check
curl -f http://localhost:5000/api/ai/health

# Detailed status check
curl -s http://localhost:5000/api/shopify/store-info | jq .
```

#### System Monitoring Script

Create `monitor.sh`:

```bash
#!/bin/bash

# Health check script
URL="http://localhost:5000/api/ai/health"
LOGFILE="/var/log/shopify-agent/health.log"

if curl -f -s $URL > /dev/null; then
    echo "$(date): Service is healthy" >> $LOGFILE
else
    echo "$(date): Service is down - restarting" >> $LOGFILE
    sudo systemctl restart shopify-agent
fi
```

### Log Management

#### Log Rotation

Create `/etc/logrotate.d/shopify-agent`:

```
/var/log/shopify-agent/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 shopify-agent shopify-agent
    postrotate
        systemctl reload shopify-agent
    endscript
}
```

### Backup Strategy

#### Database Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/shopify-agent"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup SQLite database
cp /home/shopify-agent/shopify-ai-agent/src/database/app.db \
   $BACKUP_DIR/app_db_$DATE.db

# Backup environment file
cp /home/shopify-agent/shopify-ai-agent/.env \
   $BACKUP_DIR/env_$DATE.backup

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.backup" -mtime +30 -delete
```

### Performance Optimization

#### Database Optimization

```python
# Add to main.py for production
from flask_sqlalchemy import SQLAlchemy

# Database connection pooling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 120,
    'pool_pre_ping': True
}
```

#### Caching

```python
# Add Redis caching
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@cache.memoize(timeout=300)
def get_store_info():
    # Cached store info
    pass
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Symptoms**: Service fails to start, connection refused

**Solutions**:
```bash
# Check logs
sudo journalctl -u shopify-agent -f

# Verify environment variables
sudo -u shopify-agent cat /home/shopify-agent/shopify-ai-agent/.env

# Test manually
sudo -u shopify-agent bash
cd /home/shopify-agent/shopify-ai-agent
source venv/bin/activate
python src/main.py
```

#### 2. Shopify API Errors

**Symptoms**: 401 Unauthorized, API rate limits

**Solutions**:
```bash
# Test API credentials
curl -H "X-Shopify-Access-Token: YOUR_TOKEN" \
     https://YOUR_STORE.myshopify.com/admin/api/2023-07/shop.json

# Check API scopes
# Verify token permissions in Shopify admin
```

#### 3. OpenAI API Issues

**Symptoms**: AI chat not working, API errors

**Solutions**:
```bash
# Test OpenAI API
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.openai.com/v1/models

# Check quota and billing
# Verify API key format
```

#### 4. Frontend Issues

**Symptoms**: UI not loading, JavaScript errors

**Solutions**:
```bash
# Check static files
ls -la src/static/

# Verify CORS settings
# Check browser console for errors
```

### Performance Issues

#### High Memory Usage

```bash
# Monitor memory
htop
ps aux | grep python

# Optimize Gunicorn workers
# Reduce worker count if memory constrained
```

#### Slow Response Times

```bash
# Check database performance
# Add query optimization
# Implement caching
# Monitor API rate limits
```

## Security Considerations

### Environment Security

```bash
# Secure environment file
chmod 600 .env
chown shopify-agent:shopify-agent .env

# Use secrets management in production
# Consider AWS Secrets Manager, HashiCorp Vault
```

### Network Security

```bash
# Firewall configuration
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban
```

### Application Security

```python
# Add security headers
from flask_talisman import Talisman

Talisman(app, force_https=True)

# Input validation
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

## Scaling Considerations

### Horizontal Scaling

```yaml
# Docker Swarm example
version: '3.8'
services:
  shopify-agent:
    image: shopify-agent:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

### Load Balancing

```nginx
upstream shopify_agent {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    location / {
        proxy_pass http://shopify_agent;
    }
}
```

This deployment guide provides comprehensive instructions for deploying the Shopify AI Agent in various environments, from development to production. Choose the deployment method that best fits your infrastructure and requirements.

