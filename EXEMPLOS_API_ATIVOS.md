# 📊 API de Ativos - Exemplos de Uso

## 🟢 POST `/api/ativos/cadastrar`

### Cadastrar BOVA11.SA (obrigatório para cálculos)
```bash
curl -X POST http://localhost:5000/api/ativos/cadastrar \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "ticker": "BOVA11.SA",
    "intervalo": "1d",
    "period": "3mo",
    "carteira_id": 1
  }'
```

### Cadastrar ITUB4.SA
```bash
curl -X POST http://localhost:5000/api/ativos/cadastrar \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "ticker": "ITUB4.SA",
    "intervalo": "1d",
    "period": "3mo",
    "carteira_id": 1
  }'
```

### Cadastrar PETR4.SA
```bash
curl -X POST http://localhost:5000/api/ativos/cadastrar \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "ticker": "PETR4.SA",
    "intervalo": "1d",
    "period": "3mo",
    "carteira_id": 1
  }'
```

### Resposta esperada:
```json
{
  "success": true,
  "message": "Asset ITUB4.SA processed successfully",
  "data": {
    "ticker": "ITUB4.SA",
    "carteira_id": 1,
    "total_records": 63,
    "inserted_records": 63,
    "existing_records": 0,
    "period": "3mo",
    "intervalo": "1d"
  }
}
```

## 🟡 GET `/api/carteiras/{carteira_id}/indicadores`

### Buscar indicadores da carteira
```bash
curl -X GET http://localhost:5000/api/carteiras/1/indicadores \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Resposta esperada:
```json
{
  "success": true,
  "carteira_id": 1,
  "data": {
    "ativos_ordenados": ["ITUB4.SA", "PETR4.SA", "BOVA11.SA"],
    "retorno_esperado": {
      "ITUB4.SA": 0.0012,
      "PETR4.SA": 0.0015,
      "BOVA11.SA": 0.0010
    },
    "desvio_padrao": {
      "ITUB4.SA": 0.025,
      "PETR4.SA": 0.030,
      "BOVA11.SA": 0.020
    },
    "indice_desempenho": {
      "ITUB4.SA": 0.048,
      "PETR4.SA": 0.050,
      "BOVA11.SA": 0.050
    },
    "indice_sharpe": {
      "ITUB4.SA": 0.046,
      "PETR4.SA": 0.048,
      "BOVA11.SA": 0.048
    },
    "pesos": {
      "ITUB4.SA": 0.5,
      "PETR4.SA": 0.5,
      "BOVA11.SA": 0.0
    },
    "retorno_carteira": 0.00135,
    "beta": {
      "ITUB4.SA": 1.2,
      "PETR4.SA": 1.5,
      "BOVA11.SA": 1.0
    },
    "matriz_covariancia": {
      "ITUB4.SA": {
        "ITUB4.SA": 0.000625,
        "PETR4.SA": 0.000450,
        "BOVA11.SA": 0.000400
      },
      "PETR4.SA": {
        "ITUB4.SA": 0.000450,
        "PETR4.SA": 0.000900,
        "BOVA11.SA": 0.000600
      },
      "BOVA11.SA": {
        "ITUB4.SA": 0.000400,
        "PETR4.SA": 0.000600,
        "BOVA11.SA": 0.000400
      }
    },
    "matriz_cov_customizada": {
      "ITUB4.SA": {
        "ITUB4.SA": 0.000625,
        "PETR4.SA": 0.000720,
        "BOVA11.SA": 0.000480
      },
      "PETR4.SA": {
        "ITUB4.SA": 0.000720,
        "PETR4.SA": 0.000900,
        "BOVA11.SA": 0.000600
      },
      "BOVA11.SA": {
        "ITUB4.SA": 0.000480,
        "PETR4.SA": 0.000600,
        "BOVA11.SA": 0.000400
      }
    },
    "desvio_padrao_carteira": 0.024,
    "indicadores_carteira": {
      "retorno_esperado": 0.00135,
      "variancia": 0.000576,
      "desvio_padrao": 0.024,
      "indice_desempenho": 0.056,
      "indice_sharpe": 0.054
    }
  }
}
```

## 📋 Parâmetros e Validações

### POST `/api/ativos/cadastrar`:
- **ticker** (obrigatório): Símbolo do ativo (ex: ITUB4.SA)
- **carteira_id** (obrigatório): ID da carteira (deve pertencer ao admin autenticado)
- **intervalo** (opcional): Intervalo dos dados (padrão: "1d")
- **period** (opcional): Período dos dados (padrão: "3mo" = ~90 dias)

### GET `/api/carteiras/{carteira_id}/indicadores`:
- **carteira_id** (obrigatório): ID da carteira na URL
- **Pré-requisito**: BOVA11.SA deve estar cadastrado na carteira
- **Retorna**: Todos os indicadores financeiros calculados

## ⚠️ Validações e Regras de Negócio

### ✅ Validações POST `/api/ativos/cadastrar`:
1. Ticker é obrigatório
2. Carteira ID é obrigatório
3. Carteira deve pertencer ao usuário admin autenticado
4. Não duplica dados para a mesma data
5. Busca dados dos últimos ~90 dias (period=3mo)
6. Salva apenas dados válidos do yfinance

### ✅ Validações GET `/api/carteiras/{id}/indicadores`:
1. Carteira deve pertencer ao usuário admin autenticado
2. BOVA11.SA deve estar presente na carteira
3. Pelo menos 1 ativo além do BOVA11.SA
4. Dados suficientes para cálculos estatísticos

## 🔍 Indicadores Calculados

### 📊 Por Ativo:
- **Retorno Esperado**: Média das variações % diárias
- **Desvio Padrão**: Volatilidade das variações %
- **Índice de Desempenho**: Retorno / Desvio
- **Índice de Sharpe**: (Retorno - Taxa Livre Risco) / Desvio
- **Beta**: Covariância com BOVA11 / Variância BOVA11

### 📈 Da Carteira:
- **Pesos**: Distribuição igualitária (excluindo BOVA11)
- **Retorno da Carteira**: Produto escalar (retorno × pesos)
- **Matriz de Covariância**: Covariância entre todos os ativos
- **Matriz Customizada**: Baseada no Beta e variância do BOVA11
- **Desvio Padrão da Carteira**: √(pesos^T × Cov × pesos)

## 🚀 Fluxo Recomendado de Uso

1. **Autentique-se** e obtenha JWT token
2. **Crie uma carteira** via API de carteiras
3. **Cadastre BOVA11.SA primeiro** (obrigatório)
4. **Cadastre outros ativos** (ITUB4.SA, PETR4.SA, etc.)
5. **Consulte os indicadores** da carteira completa

## 📝 Notas Técnicas

- **yfinance**: Busca dados históricos automaticamente
- **pandas**: Calcula estatísticas e matrizes
- **numpy**: Operações matriciais e produto escalar
- **SQLAlchemy**: Persiste dados com chaves estrangeiras
- **Anti-duplicação**: Verifica antes de inserir novos dados
- **Segurança**: Apenas admin vê suas próprias carteiras
