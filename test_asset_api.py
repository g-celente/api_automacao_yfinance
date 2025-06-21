#!/usr/bin/env python3
"""
Script de teste para as funcionalidades de API de ativos.
Testa os endpoints de cadastro de ativos e cálculo de indicadores.
"""

import requests
import json
import time
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

class AssetAPITester:
    def __init__(self):
        self.token = None
        self.carteira_id = None
        self.session = requests.Session()
        
    def authenticate(self):
        """Autentica o usuário admin e obtém o token JWT."""
        print("🔐 Autenticando usuário admin...")
        
        # Primeiro, registrar o admin (se não existir)
        register_data = {
            "name": "Admin Teste",
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/api/register", json=register_data)
        if response.status_code == 201:
            print("✅ Admin registrado com sucesso")
        else:
            print(f"ℹ️ Admin já existe ou erro no registro: {response.status_code}")
        
        # Fazer login
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/api/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
            print(f"✅ Login realizado com sucesso. Token: {self.token[:20]}...")
            
            # Configurar headers para próximas requisições
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            })
            return True
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return False
    
    def create_test_client(self):
        """Cria um cliente de teste."""
        print("\n👤 Criando cliente de teste...")
        
        client_data = {
            "name": "Cliente Teste",
            "email": "cliente@teste.com",
            "phone": "11999999999"
        }
        
        response = self.session.post(f"{BASE_URL}/api/clients", json=client_data)
        
        if response.status_code == 201:
            data = response.json()
            client_id = data.get('client', {}).get('id')
            print(f"✅ Cliente criado com sucesso. ID: {client_id}")
            return client_id
        else:
            print(f"❌ Erro ao criar cliente: {response.status_code} - {response.text}")
            return None
    
    def create_test_portfolio(self, client_id):
        """Cria uma carteira de teste."""
        print("\n💼 Criando carteira de teste...")
        
        portfolio_data = {
            "name": "Carteira Teste",
            "description": "Carteira para testes de API",
            "cliente_id": client_id
        }
        
        response = self.session.post(f"{BASE_URL}/api/wallets", json=portfolio_data)
        
        if response.status_code == 201:
            data = response.json()
            portfolio_id = data.get('portfolio', {}).get('id')
            print(f"✅ Carteira criada com sucesso. ID: {portfolio_id}")
            self.carteira_id = portfolio_id
            return portfolio_id
        else:
            print(f"❌ Erro ao criar carteira: {response.status_code} - {response.text}")
            return None
    
    def test_cadastrar_ativo(self, ticker, carteira_id):
        """Testa o cadastro de um ativo."""
        print(f"\n📈 Testando cadastro do ativo {ticker}...")
        
        asset_data = {
            "ticker": ticker,
            "intervalo": "1d",
            "period": "3mo",
            "carteira_id": carteira_id
        }
        
        response = self.session.post(f"{BASE_URL}/api/assets", json=asset_data)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Ativo {ticker} cadastrado com sucesso")
            print(f"   📊 Registros inseridos: {data.get('data', {}).get('records_inserted', 0)}")
            print(f"   🔄 Registros duplicados: {data.get('data', {}).get('existing_records', 0)}")
            return True
        else:
            print(f"❌ Erro ao cadastrar ativo {ticker}: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    
    def test_indicadores_carteira(self, carteira_id):
        """Testa o cálculo de indicadores da carteira."""
        print(f"\n📊 Testando cálculo de indicadores para carteira {carteira_id}...")
        
        response = self.session.get(f"{BASE_URL}/api/assets/{carteira_id}/indicadores")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Indicadores calculados com sucesso")
            
            # Exibir alguns indicadores principais
            indicadores = data.get('data', {})
            print(f"   📈 Retorno da carteira: {indicadores.get('retorno_carteira', 'N/A'):.4f}")
            print(f"   📊 Desvio padrão da carteira: {indicadores.get('desvio_padrao_carteira', 'N/A'):.4f}")
            
            # Mostrar indicadores dos ativos
            retornos = indicadores.get('retorno_esperado', {})
            betas = indicadores.get('beta', {})
            
            print("   🏢 Indicadores por ativo:")
            for ticker in indicadores.get('ativos_ordenados', []):
                retorno = retornos.get(ticker, 0)
                beta = betas.get(ticker, 0)
                print(f"      {ticker}: Retorno={retorno:.4f}, Beta={beta:.4f}")
            
            return True
        else:
            print(f"❌ Erro ao calcular indicadores: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    
    def run_tests(self):
        """Executa todos os testes."""
        print("🚀 Iniciando testes da API de Ativos")
        print("=" * 50)
        
        # Autenticar
        if not self.authenticate():
            print("❌ Falha na autenticação. Parando testes.")
            return False
        
        # Criar cliente
        client_id = self.create_test_client()
        if not client_id:
            print("❌ Falha ao criar cliente. Parando testes.")
            return False
        
        # Criar carteira
        portfolio_id = self.create_test_portfolio(client_id)
        if not portfolio_id:
            print("❌ Falha ao criar carteira. Parando testes.")
            return False
        
        # Cadastrar BOVA11.SA (obrigatório)
        print("\n🎯 Cadastrando ativo de referência (BOVA11.SA)...")
        success = self.test_cadastrar_ativo("BOVA11.SA", portfolio_id)
        if not success:
            print("❌ Falha ao cadastrar BOVA11.SA. Parando testes.")
            return False
        
        # Aguardar um pouco para evitar rate limit
        time.sleep(2)
        
        # Cadastrar outros ativos
        ativos_teste = ["ITUB4.SA", "PETR4.SA", "VALE3.SA"]
        
        for ticker in ativos_teste:
            success = self.test_cadastrar_ativo(ticker, portfolio_id)
            if success:
                time.sleep(1)  # Aguardar para evitar rate limit
        
        # Aguardar um pouco antes de calcular indicadores
        time.sleep(2)
        
        # Calcular indicadores
        self.test_indicadores_carteira(portfolio_id)
        
        print("\n" + "=" * 50)
        print("🎉 Testes concluídos!")
        return True

def main():
    """Função principal."""
    tester = AssetAPITester()
    
    try:
        tester.run_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante os testes: {str(e)}")

if __name__ == "__main__":
    main()
