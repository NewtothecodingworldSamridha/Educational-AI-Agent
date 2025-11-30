# Deployment Guide

This guide covers deploying the Educational AI Agent to various platforms.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Production Checklist](#production-checklist)
- [Monitoring](#monitoring)

## Prerequisites

### Required
- Docker & Docker Compose
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### API Keys
- Anthropic API key (required)
- Brave Search API key (optional, for web search)

### Infrastructure
- Minimum 2GB RAM
- 2 CPU cores
- 20GB storage
- SSL certificate (for production)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/educational-ai-agent.git
cd educational-ai-agent
```

### 2. Configure Environment Variables

Create `.env` files in backend and frontend:

**backend/.env**
```bash
# Copy from .env.example
cp backend/.env.example backend/.env

# Edit with your values
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@host:5432/eduai
REDIS_URL=redis://host:6379/0
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
DEBUG=false
```

**frontend/.env**
```bash
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_WS_URL=wss://api.yourdomain.com
```

## Docker Deployment

### Development
```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production
```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale backend=3
```

## Cloud Platforms

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Build and push images**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URL

# Build and tag
docker build -t eduai-backend:latest ./backend
docker tag eduai-backend:latest YOUR_ECR_URL/eduai-backend:latest

# Push
docker push YOUR_ECR_URL/eduai-backend:latest
```

2. **Create ECS Task Definition**
```json
{
  "family": "eduai-backend",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_ECR_URL/eduai-backend:latest",
      "memory": 2048,
      "cpu": 1024,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"}
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:..."
        }
      ]
    }
  ]
}
```

3. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster eduai-cluster \
  --service-name eduai-backend \
  --task-definition eduai-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### Using EC2

1. **Launch EC2 instance**
   - Amazon Linux 2023
   - t3.medium or larger
   - Configure security groups (80, 443, 22)

2. **Install dependencies**
```bash
sudo yum update -y
sudo yum install docker git -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. **Deploy application**
```bash
git clone https://github.com/yourusername/educational-ai-agent.git
cd educational-ai-agent
cp backend/.env.example backend/.env
# Edit .env with production values
docker-compose -f docker-compose.prod.yml up -d
```

4. **Setup Nginx reverse proxy**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Google Cloud Platform (GCP)

#### Using Cloud Run

1. **Build and push to GCR**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/eduai-backend ./backend
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy eduai-backend \
  --image gcr.io/PROJECT_ID/eduai-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets ANTHROPIC_API_KEY=anthropic-key:latest
```

### Azure

#### Using Azure Container Instances

1. **Create resource group**
```bash
az group create --name eduai-resources --location eastus
```

2. **Deploy container**
```bash
az container create \
  --resource-group eduai-resources \
  --name eduai-backend \
  --image YOUR_ACR.azurecr.io/eduai-backend:latest \
  --dns-name-label eduai-backend \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production \
  --secure-environment-variables ANTHROPIC_API_KEY=$ANTHROPIC_KEY
```

### Heroku

1. **Install Heroku CLI and login**
```bash
heroku login
```

2. **Create app**
```bash
heroku create eduai-backend
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
```

3. **Set environment variables**
```bash
heroku config:set ANTHROPIC_API_KEY=your-key
heroku config:set ENVIRONMENT=production
```

4. **Deploy**
```bash
git push heroku main
```

### DigitalOcean

#### Using App Platform

1. **Create app.yaml**
```yaml
name: eduai
services:
- name: backend
  github:
    repo: yourusername/educational-ai-agent
    branch: main
    deploy_on_push: true
  source_dir: backend
  envs:
  - key: ANTHROPIC_API_KEY
    scope: RUN_TIME
    type: SECRET
  - key: ENVIRONMENT
    value: production
  http_port: 8000
  instance_count: 2
  instance_size_slug: basic-xs

databases:
- name: eduai-db
  engine: PG
  version: "14"

- name: eduai-redis
  engine: REDIS
  version: "7"
```

2. **Deploy**
```bash
doctl apps create --spec app.yaml
```

## Production Checklist

### Security
- [ ] Use HTTPS/TLS for all connections
- [ ] Set secure SECRET_KEY
- [ ] Enable CORS only for trusted origins
- [ ] Use secrets manager for API keys
- [ ] Enable rate limiting
- [ ] Setup firewall rules
- [ ] Regular security updates
- [ ] Enable database encryption
- [ ] Setup backup encryption

### Performance
- [ ] Enable Redis caching
- [ ] Setup CDN for static assets
- [ ] Configure database connection pooling
- [ ] Enable gzip compression
- [ ] Optimize Docker images (multi-stage builds)
- [ ] Setup horizontal scaling
- [ ] Configure load balancer
- [ ] Database indexing

### Monitoring
- [ ] Setup error tracking (Sentry)
- [ ] Configure logging (CloudWatch, Stackdriver)
- [ ] Enable metrics (Prometheus)
- [ ] Setup dashboards (Grafana)
- [ ] Configure alerts
- [ ] Monitor API response times
- [ ] Track database performance
- [ ] Setup uptime monitoring

### Reliability
- [ ] Configure auto-scaling
- [ ] Setup health checks
- [ ] Enable automatic restarts
- [ ] Configure backup strategy
- [ ] Test disaster recovery
- [ ] Setup rollback procedures
- [ ] Document incident response

### Data
- [ ] Configure database backups
- [ ] Setup replication
- [ ] Enable point-in-time recovery
- [ ] Data retention policies
- [ ] GDPR compliance (if applicable)
- [ ] Student data privacy

## Monitoring

### Prometheus & Grafana

1. **Start monitoring stack**
```bash
docker-compose --profile monitoring up -d
```

2. **Access dashboards**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

3. **Import dashboards**
- Application metrics
- Database performance
- API response times
- Error rates

### Application Logs

**View logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/api/health

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping
```

## Troubleshooting

### Common Issues

**Database connection errors**
```bash
# Check database is running
docker-compose ps postgres

# Check connection from backend
docker-compose exec backend python -c "import psycopg2; print('OK')"

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

**High memory usage**
```bash
# Check container stats
docker stats

# Restart services
docker-compose restart backend

# Scale down if needed
docker-compose up -d --scale backend=1
```

**API errors**
```bash
# Check logs
docker-compose logs backend --tail=50

# Check environment variables
docker-compose exec backend env | grep ANTHROPIC

# Test API directly
curl http://localhost:8000/api/health
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend instances
docker-compose up -d --scale backend=5

# With load balancer
# Add nginx configuration for load balancing
```

### Vertical Scaling

Update docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Backup & Recovery

### Database Backup

```bash
# Manual backup
docker-compose exec postgres pg_dump -U eduai eduai_db > backup.sql

# Automated backup (cron)
0 2 * * * docker-compose exec postgres pg_dump -U eduai eduai_db | gzip > /backups/$(date +\%Y\%m\%d).sql.gz
```

### Restore

```bash
# Restore from backup
docker-compose exec -T postgres psql -U eduai eduai_db < backup.sql
```

## Support

For deployment issues:
- GitHub Issues: https://github.com/yourusername/educational-ai-agent/issues
- Email: support@eduai.org
- Documentation: https://docs.eduai.org
