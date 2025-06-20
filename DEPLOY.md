# Deploy na Render - Guia Completo

## 📋 Pré-requisitos

1. Conta na [Render](https://render.com)
2. Repositório GitHub/GitLab com o código
3. Banco de dados PostgreSQL configurado

## 🚀 Passos para Deploy

### 1. Configuração no Render Dashboard

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub/GitLab

### 2. Configurações do Serviço

- **Name**: `investment-api`
- **Environment**: `Python 3`
- **Build Command**: `./build.sh` (ou deixe vazio)
- **Start Command**: `gunicorn app:app`
- **Plan**: Free (ou conforme necessário)

### 3. Variáveis de Ambiente Obrigatórias

Configure estas variáveis no painel da Render:

```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600
WEB_CONCURRENCY=4
PORT=10000
LOG_LEVEL=info
```

### 4. Banco de Dados

Se usar PostgreSQL da Render:
1. Crie um banco PostgreSQL na Render
2. Use a CONNECTION STRING fornecida como DATABASE_URL

Se usar banco externo (como Neon):
1. Use sua string de conexão existente
2. Certifique-se que aceita conexões externas

### 5. Redis (Opcional)

Se usar Redis:
1. Crie um serviço Redis na Render
2. Configure REDIS_URL com a string de conexão

## ⚡ Deploy Automático

Após configurar:
1. Faça push para o branch principal
2. Render automaticamente fará o deploy
3. Monitore os logs durante o processo

## 🔍 Verificação

Após o deploy:
- Acesse: `https://your-app-name.onrender.com/health`
- Deve retornar: `{"status": "healthy", "service": "investment-api"}`

## 📝 Comandos Locais para Teste

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis
export FLASK_ENV=production
export DATABASE_URL=your-database-url

# Executar migrações
flask db upgrade

# Testar com Gunicorn
gunicorn app:app --bind 0.0.0.0:8000
```

## 🐛 Troubleshooting

### Erro de Importação
- Verifique se o arquivo `app.py` está na raiz
- Confirme que `create_app()` está funcionando

### Erro de Banco
- Verifique DATABASE_URL
- Execute migrações: `flask db upgrade`

### Erro de Build
- Verifique `requirements.txt`
- Confirme que `build.sh` tem permissões de execução

## 📊 Monitoramento

- Logs: Dashboard da Render → Logs
- Métricas: Dashboard da Render → Metrics
- Health: `GET /health`

## 🔄 Updates

Para atualizar a aplicação:
1. Faça push das mudanças
2. Render automaticamente redeploy
3. Zero downtime deploy
