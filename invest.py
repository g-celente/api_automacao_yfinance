import requests
import pandas as pd

api_key = 'AOJ682RAC9UM47MJ'
symbol = 'PETR4.SAO'

url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol={symbol}&apikey={api_key}'
r = requests.get(url)
data = r.json()

# Acessa apenas a parte com os dados de tempo
time_series = data.get("Weekly Adjusted Time Series", {})

# Converte o dicionário de datas em DataFrame
df = pd.DataFrame.from_dict(time_series, orient='index')

# Renomeia colunas para facilitar leitura
df = df.rename(columns={
    '1. open': 'abertura',
    '2. high': 'maximo',
    '3. low': 'minimo',
    '4. close': 'fechamento',
    '5. adjusted close': 'ajustado',
    '6. volume': 'volume',
    '7. dividend amount': 'dividendo'
})

to_csv = df.to_excel('PETR4_weekly_data.xlsx')

