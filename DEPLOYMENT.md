# Guia de Deploy - FIAP X Video Processor

## Visão Geral

Este documento fornece instruções detalhadas para deploy do sistema FIAP X Video Processor em diferentes ambientes.

## Pré-requisitos

### Software Necessário
- Docker 20.10+
- Docker Compose 2.0+
- Git
- 4GB RAM mínimo
- 20GB espaço em disco

### Portas Utilizadas
- 3000: Frontend (React)
- 8080: API Gateway
- 8001: Auth Service
- 5432: PostgreSQL
- 6379: Redis
- 5672: RabbitMQ
- 15672: RabbitMQ Management
- 9090: Prometheus
- 3001: Grafana

## Deploy Local (Desenvolvimento)

### 1. Clone do Repositório
```bash
git clone <repository-url>
cd fiapx-video-processor
```

### 2. Configuração do Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações (opcional)
nano .env
```

### 3. Executar Setup Automático
```bash
# Dar permissão de execução
chmod +x scripts/setup-dev.sh

# Executar setup
./scripts/setup-dev.sh
```

### 4. Verificar Serviços
```bash
# Verificar status dos containers
docker-compose ps

# Verificar logs
docker-compose logs -f

# Executar testes
./scripts/test-system.sh
```

## Deploy em Produção

### 1. Preparação do Servidor

#### Instalação do Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Configuração do Firewall
```bash
# Permitir portas necessárias
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

### 2. Configuração de Produção

#### Arquivo .env para Produção
```bash
# Database Configuration
POSTGRES_DB=fiapx_videos_prod
POSTGRES_USER=fiapx_prod_user
POSTGRES_PASSWORD=<strong-password>

# RabbitMQ Configuration
RABBITMQ_DEFAULT_USER=fiapx_prod_user
RABBITMQ_DEFAULT_PASS=<strong-password>

# JWT Secret
JWT_SECRET=test_secret

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<your-email>
SMTP_PASSWORD=<app-password>

# Service URLs
AUTH_SERVICE_URL=http://auth-service:8000
VIDEO_PROCESSOR_URL=http://video-processor:8000

# Redis Configuration
REDIS_URL=redis://redis:6379

# RabbitMQ URL
RABBITMQ_URL=amqp://fiapx_prod_user:<strong-password>@rabbitmq:5672/

# Database URL
DATABASE_URL=postgresql://fiapx_prod_user:<strong-password>@postgres:5432/fiapx_videos_prod
```

#### Docker Compose para Produção
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Override configurations for production
  postgres:
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: always

  redis:
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}

  rabbitmq:
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_DEFAULT_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_DEFAULT_PASS}
    restart: always

  auth-service:
    restart: always
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      JWT_SECRET: ${JWT_SECRET}

  video-processor:
    restart: always
    environment:
      DATABASE_URL: ${DATABASE_URL}
      RABBITMQ_URL: ${RABBITMQ_URL}
      REDIS_URL: ${REDIS_URL}

  notification-service:
    restart: always
    environment:
      RABBITMQ_URL: ${RABBITMQ_URL}
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}

  api-gateway:
    restart: always
    environment:
      AUTH_SERVICE_URL: ${AUTH_SERVICE_URL}
      VIDEO_PROCESSOR_URL: ${VIDEO_PROCESSOR_URL}
      REDIS_URL: ${REDIS_URL}

  frontend:
    restart: always

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api-gateway
      - frontend
    restart: always

volumes:
  postgres_data_prod:
```

### 3. Deploy em Produção

#### Build e Deploy
```bash
# Build das imagens
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verificar status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

#### Configuração do Nginx (Opcional)
```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api-gateway:8000;
    }

    upstream frontend_backend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # API routes
        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            client_max_body_size 500M;
            proxy_read_timeout 300s;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Deploy na AWS

### 1. Preparação da Infraestrutura

#### EC2 Instance
```bash
# Criar instância EC2 (t3.medium ou superior)
# Ubuntu 22.04 LTS
# Security Group: permitir portas 80, 443, 22

# Conectar via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip
```

#### RDS PostgreSQL (Opcional)
```bash
# Criar instância RDS PostgreSQL
# Configurar security group para permitir conexão da EC2
# Atualizar DATABASE_URL no .env
```

#### ElastiCache Redis (Opcional)
```bash
# Criar cluster ElastiCache Redis
# Configurar security group
# Atualizar REDIS_URL no .env
```

### 2. Deploy na EC2

#### Instalação e Configuração
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone do projeto
git clone <repository-url>
cd fiapx-video-processor

# Configurar ambiente
cp .env.example .env
nano .env  # Editar com configurações da AWS

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Deploy no Kubernetes

### 1. Preparação dos Manifestos

#### Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fiapx-video-processor
```

#### ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fiapx-config
  namespace: fiapx-video-processor
data:
  POSTGRES_DB: "fiapx_videos"
  REDIS_URL: "redis://redis:6379"
  # ... outras configurações
```

#### Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: fiapx-secrets
  namespace: fiapx-video-processor
type: Opaque
data:
  POSTGRES_PASSWORD: <base64-encoded>
  JWT_SECRET: <base64-encoded>
  # ... outros secrets
```

### 2. Deploy dos Serviços

#### PostgreSQL
```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: fiapx-video-processor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: fiapx-secrets
              key: POSTGRES_PASSWORD
        # ... outras configurações
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: fiapx-video-processor
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

#### Aplicação
```bash
# Aplicar manifestos
kubectl apply -f k8s/

# Verificar status
kubectl get pods -n fiapx-video-processor

# Verificar logs
kubectl logs -f deployment/api-gateway -n fiapx-video-processor
```

## Monitoramento e Logs

### 1. Verificação de Saúde

#### Health Checks
```bash
# Verificar saúde dos serviços
curl http://localhost:8080/api/health/all

# Verificar métricas
curl http://localhost:9090/metrics
```

#### Logs
```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f api-gateway

# Ver logs com timestamp
docker-compose logs -f -t
```

### 2. Alertas e Notificações

#### Configuração do Grafana
1. Acessar http://localhost:3001
2. Login: admin/admin
3. Configurar datasource Prometheus
4. Importar dashboards
5. Configurar alertas

## Backup e Recovery

### 1. Backup do Banco de Dados

#### Backup Manual
```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U fiapx_user fiapx_videos > backup.sql

# Backup Redis
docker-compose exec redis redis-cli BGSAVE
```

#### Backup Automático
```bash
# Script de backup automático
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U fiapx_user fiapx_videos > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://your-backup-bucket/
```

### 2. Recovery

#### Restore PostgreSQL
```bash
# Restore do backup
docker-compose exec -T postgres psql -U fiapx_user fiapx_videos < backup.sql
```

## Troubleshooting

### Problemas Comuns

#### Serviços não iniciam
```bash
# Verificar logs
docker-compose logs

# Verificar recursos
docker system df
docker system prune

# Reiniciar serviços
docker-compose restart
```

#### Problemas de conectividade
```bash
# Verificar rede
docker network ls
docker network inspect fiapx-video-processor_fiapx-network

# Testar conectividade
docker-compose exec api-gateway ping postgres
```

#### Performance issues
```bash
# Verificar recursos
docker stats

# Verificar métricas
curl http://localhost:9090/metrics
```

## Segurança

### 1. Hardening

#### Configurações de Segurança
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Configurar firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Configurar fail2ban
sudo apt install fail2ban
```

#### Secrets Management
```bash
# Usar Docker secrets em produção
echo "strong-password" | docker secret create postgres_password -

# Ou usar ferramentas como HashiCorp Vault
```

### 2. SSL/TLS

#### Certificados Let's Encrypt
```bash
# Instalar certbot
sudo apt install certbot

# Obter certificado
sudo certbot certonly --standalone -d your-domain.com

# Configurar renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Conclusão

Este guia fornece instruções completas para deploy do sistema FIAP X Video Processor em diferentes ambientes. Para produção, sempre considere:

- Usar senhas fortes
- Configurar SSL/TLS
- Implementar backup automático
- Monitorar recursos e performance
- Manter sistema atualizado
- Implementar logging centralizado
- Configurar alertas automáticos

Para suporte adicional, consulte a documentação específica de cada componente ou entre em contato com a equipe de desenvolvimento.

