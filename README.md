# FIAP X - Sistema de Processamento de Vídeos

Sistema de processamento de vídeos desenvolvido com arquitetura de microsserviços para o HackSOAT10.

## 🏗️ Arquitetura

O sistema é composto pelos seguintes microsserviços:

- **API Gateway**: Ponto de entrada único para todas as requisições
- **Auth Service**: Serviço de autenticação e autorização com JWT
- **Video Processor**: Serviço de processamento de vídeos com FFmpeg
- **Notification Service**: Serviço de notificações por email
- **Frontend**: Interface web em React
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache e sessões
- **RabbitMQ**: Sistema de mensageria para processamento assíncrono
- **Prometheus + Grafana**: Monitoramento e métricas

## 🚀 Funcionalidades

### Funcionalidades Essenciais
- ✅ Processamento de múltiplos vídeos simultaneamente
- ✅ Sistema de filas para evitar perda de requisições em picos
- ✅ Autenticação com usuário e senha
- ✅ Listagem de status dos vídeos por usuário
- ✅ Notificações por email em caso de erro ou sucesso

### Requisitos Técnicos
- ✅ Persistência de dados (PostgreSQL + Redis)
- ✅ Arquitetura escalável com microsserviços
- ✅ Versionamento no GitHub
- ✅ Testes automatizados
- ✅ CI/CD com GitHub Actions
- ✅ Containerização com Docker
- ✅ Orquestração com Docker Compose
- ✅ Mensageria com RabbitMQ
- ✅ Monitoramento com Prometheus + Grafana

## 🛠️ Stack Tecnológica

- **Backend**: Python + Flask
- **Frontend**: React + Tailwind CSS + shadcn/ui
- **Banco de Dados**: PostgreSQL + Redis
- **Mensageria**: RabbitMQ
- **Processamento**: FFmpeg
- **Containers**: Docker + Docker Compose
- **Monitoramento**: Prometheus + Grafana
- **CI/CD**: GitHub Actions

## 📋 Pré-requisitos

- Docker
- Docker Compose
- Git

## 🚀 Como Executar

### 1. Clone o repositório
```bash
git clone <repository-url>
cd fiapx-video-processor
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 3. Execute o sistema
```bash
docker-compose up -d
```

### 4. Acesse os serviços

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **RabbitMQ Management**: http://localhost:15672 (user: fiapx_user, pass: fiapx_password)
- **Grafana**: http://localhost:3001 (user: admin, pass: admin)
- **Prometheus**: http://localhost:9090

## 👥 Usuários de Teste

O sistema vem com usuários pré-configurados:

- **Admin**: username: `admin`, password: `admin123`
- **Teste**: username: `testuser`, password: `test123`

## 📊 Monitoramento

### Prometheus
- Coleta métricas de todos os serviços
- Health checks automáticos
- Alertas configuráveis

### Grafana
- Dashboards para visualização de métricas
- Monitoramento em tempo real
- Alertas visuais

## 🔧 Desenvolvimento

### Estrutura do Projeto
```
fiapx-video-processor/
├── api-gateway/          # API Gateway service
├── auth-service/         # Authentication service
├── video-processor/      # Video processing service
├── notification-service/ # Notification service
├── frontend/            # React frontend
├── database/            # Database initialization scripts
├── monitoring/          # Prometheus and Grafana configs
├── scripts/             # Utility scripts
└── docker-compose.yml   # Docker Compose configuration
```

### Executar Serviços Individualmente

#### Auth Service
```bash
cd auth-service
source venv/bin/activate
python src/main.py
```

#### Video Processor
```bash
cd video-processor
source venv/bin/activate
python src/main.py
```

#### Frontend
```bash
cd frontend
pnpm install
pnpm run dev
```

## 🧪 Testes

### Executar Testes Unitários
```bash
# Para cada serviço
cd <service-directory>
source venv/bin/activate
python -m pytest tests/
```

### Testes de Integração
```bash
# Execute o sistema completo
docker-compose up -d

# Execute os testes de integração
./scripts/run-integration-tests.sh
```

## 📦 Deploy

### Produção com Docker Compose
```bash
# Build das imagens
docker-compose build

# Deploy em produção
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### CI/CD
O projeto inclui workflows do GitHub Actions para:
- Testes automatizados
- Build das imagens Docker
- Deploy automático

## 🔒 Segurança

- Autenticação JWT
- Validação de tipos de arquivo
- Rate limiting
- CORS configurado
- Headers de segurança
- Usuários não-root nos containers

## 📈 Escalabilidade

- Microsserviços independentes
- Load balancing no API Gateway
- Processamento assíncrono com filas
- Cache com Redis
- Horizontal scaling ready

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco de dados**
   ```bash
   docker-compose logs postgres
   ```

2. **Problemas com RabbitMQ**
   ```bash
   docker-compose logs rabbitmq
   ```

3. **Erro no processamento de vídeo**
   ```bash
   docker-compose logs video-processor
   ```

### Logs
```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f <service-name>
```

## 📝 API Documentation

### Autenticação
- `POST /api/auth/register` - Registrar usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/verify` - Verificar token
- `GET /api/auth/profile` - Perfil do usuário

### Processamento de Vídeos
- `POST /api/video/upload` - Upload de vídeo
- `GET /api/video/jobs` - Listar jobs
- `GET /api/video/jobs/{id}` - Detalhes do job
- `GET /api/video/jobs/{id}/download` - Download do resultado
- `GET /api/video/stats` - Estatísticas do usuário

### Health Checks
- `GET /api/health` - Health check do serviço
- `GET /api/health/all` - Health check de todos os serviços

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Equipe

- Desenvolvido para o HackSOAT10 - FIAP
- Arquitetura de Microsserviços
- Boas Práticas de DevOps

