# Script PowerShell para executar o ambiente de desenvolvimento e testes

Write-Host "🚀 Configurando ambiente de desenvolvimento..." -ForegroundColor Green

# Instalar dependências
Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

# Executar migrações
Write-Host "🗄️ Executando migrações..." -ForegroundColor Yellow
flask db upgrade

# Iniciar servidor Flask em background
Write-Host "🌐 Iniciando servidor Flask..." -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock { python wsgi.py }

# Aguardar servidor iniciar
Write-Host "⏳ Aguardando servidor inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    # Executar testes
    Write-Host "🧪 Executando testes da API..." -ForegroundColor Yellow
    python test_asset_api.py
}
finally {
    # Parar servidor
    Write-Host "🛑 Parando servidor..." -ForegroundColor Yellow
    Stop-Job $serverJob
    Remove-Job $serverJob
}

Write-Host "✅ Concluído!" -ForegroundColor Green
