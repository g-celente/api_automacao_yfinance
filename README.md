# Sistema de Administração de Carteiras de Investimento

Sistema web para administração e análise de carteiras de investimento, desenvolvido com Python/Flask e arquitetura MVC.

## 🚀 Tecnologias

- **Backend:** Python 3.11+ com Flask
- **Banco de Dados:** PostgreSQL (via SQLAlchemy)
- **ORM:** SQLAlchemy + Alembic (migrações)
- **Autenticação:** JWT (JSON Web Tokens)
- **Deploy:** Docker + AWS ECS
- **Dados Externos:** Yahoo Finance API (planejado)
- **Armazenamento:** Amazon S3 (planejado)

## 📋 Pré-requisitos

- Python 3.11+
- PostgreSQL
- Docker e Docker Compose (para deploy)

## 🔧 Instalação Local

1. Clone o repositório:
```bash
git clone [seu-repositorio]
cd automacao_python
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
.\venv\Scripts\Activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
Copy .env.example to .env
# Edite as variáveis conforme necessário
```

5. Execute as migrações:
```bash
flask db upgrade
```

6. Inicie o servidor:
```bash
flask run
```

## 🐳 Rodando com Docker

1. Build da imagem:
```bash
docker-compose build
```

2. Iniciando os containers:
```bash
docker-compose up
```

## 📚 API Endpoints

### Autenticação

#### Login
```http
POST /api/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "senha123"
}
```

#### Registro
```http
POST /api/register
Content-Type: application/json

{
    "name": "User Name",
    "email": "user@example.com",
    "password": "senha123"
}
```

## 🔐 Níveis de Acesso

- **Admin:** Acesso completo ao sistema
- **Cliente:** Gerenciamento de carteiras próprias

## 📈 Funcionalidades

- Autenticação JWT
- Gestão de usuários (Admin/Cliente)
- Gerenciamento de carteiras
- Análise de ativos
- Integração com Yahoo Finance (planejado)
- Exportação de relatórios (planejado)

## 🏗️ Estrutura do Projeto

```
automacao_python/
├── app/
│   ├── controllers/     # Controladores da aplicação
│   ├── models/         # Modelos do banco de dados
│   ├── services/       # Lógica de negócios
│   └── utils/          # Utilitários
├── migrations/         # Migrações do banco de dados
├── config.py          # Configurações da aplicação
├── Dockerfile         # Configuração Docker
└── docker-compose.yml # Configuração Docker Compose
```

## 🚀 Deploy

O projeto está configurado para deploy na AWS ECS usando Docker containers.

### Processo de Deploy

1. Build da imagem Docker
2. Push para Amazon ECR
3. Deploy via ECS Task Definition
4. Configuração do load balancer

## 📝 Roadmap

- [ ] Implementar testes automatizados
- [ ] Adicionar CI/CD pipeline
- [ ] Integrar Yahoo Finance API
- [ ] Implementar cache com Redis
- [ ] Adicionar logging estruturado
- [ ] Implementar rate limiting
- [ ] Adicionar monitoramento com CloudWatch

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📜 Licença

Este projeto está sob a licença MIT.
