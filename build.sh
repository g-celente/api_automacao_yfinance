#!/bin/bash
# Build script para Render

echo "🚀 Iniciando build para Render..."

# Instala dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Executa migrações
echo "🗄️ Executando migrações do banco..."
flask db upgrade

echo "✅ Build concluído com sucesso!"
