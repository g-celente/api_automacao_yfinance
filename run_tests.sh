#!/bin/bash

# Script para executar o ambiente de desenvolvimento e testes

echo "🚀 Configurando ambiente de desenvolvimento..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Executar migrações
echo "🗄️ Executando migrações..."
flask db upgrade

# Iniciar servidor Flask em background
echo "🌐 Iniciando servidor Flask..."
python wsgi.py &
SERVER_PID=$!

# Aguardar servidor iniciar
echo "⏳ Aguardando servidor inicializar..."
sleep 5

# Executar testes
echo "🧪 Executando testes da API..."
python test_asset_api.py

# Parar servidor
echo "🛑 Parando servidor..."
kill $SERVER_PID

echo "✅ Concluído!"
