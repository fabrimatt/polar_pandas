import pandas as pd
import polars as pl
import time
import os

# --- Preparação: Criar um arquivo CSV grande para demonstração ---
# (Este bloco não seria enviado, mas é para você testar e gerar o arquivo)
# Se você já tem um arquivo de 1GB, pode pular esta parte.
# Este exemplo cria um arquivo menor para facilitar o teste rápido.
print("Criando arquivo CSV de exemplo (pode levar um tempo)...")
num_rows = 1_000_000 # Para um arquivo de 1GB, seriam muito mais linhas
data = {
    'id': range(num_rows),
    'nome': [f'Item_{i}' for i in range(num_rows)],
    'categoria': [f'Cat_{i % 10}' for i in range(num_rows)],
    'valor': [float(i * 10) for i in range(num_rows)],
    'data': [f'2025-01-{i % 28 + 1:02d}' for i in range(num_rows)]
}
df_pandas_temp = pd.DataFrame(data)
df_pandas_temp.to_csv('dados_exemplo.csv', index=False)
print(f"Arquivo 'dados_exemplo.csv' criado com {num_rows} linhas.")
# --- Fim da preparação ---


# --- 2. Lê CSV (Polars vs Pandas) ---
print("\n--- Comparando leitura de CSV ---")
csv_file = 'dados_exemplo.csv' # Use 'dados_1gb.csv' se tiver um maior

# ANTES — Pandas
print("Lendo com Pandas...")
start_time = time.time()
df_pandas = pd.read_csv(csv_file)
end_time = time.time()
print(f"Pandas levou: {end_time - start_time:.2f} segundos")
# print(df_pandas.head()) # Descomente para ver o início do DataFrame

# DEPOIS — Polars ⚡
print("Lendo com Polars...")
start_time = time.time()
df_polars = pl.read_csv(csv_file)
end_time = time.time()
print(f"Polars levou: {end_time - start_time:.2f} segundos")
# print(df_polars.head()) # Descomente para ver o início do DataFrame


# --- 3. Transformação fluent com Polars ---
print("\n--- Demonstração de transformação fluent com Polars ---")
print("Aplicando filtro, agrupamento e ordenação...")

# Certificando que a coluna 'data' é do tipo Date para o filtro
df_polars_transformed = df_polars.with_columns(
    pl.col('data').str.strptime(pl.Date, '%Y-%m-%d').alias('data_date')
)

df_result = (
    df_polars_transformed
    .filter(pl.col('data_date') >= pl.Date(2025, 1, 15)) # Exemplo com data específica
    .group_by('categoria')
    .agg(pl.col('valor').sum().alias('total_valor'))
    .sort('total_valor', descending=True)
)
print("Resultado da transformação:")
print(df_result)


# --- 4. Lazy evaluation (Big Data) com Polars ---
print("\n--- Demonstração de Lazy Evaluation com Polars ---")
print("Definindo plano de execução para um arquivo grande (simulado)...")

# Simula um arquivo muito grande que não seria carregado de uma vez
# Usaremos o mesmo arquivo de exemplo, mas a ideia é mostrar o conceito
query = (
    pl.scan_csv(csv_file)  # Não carrega tudo para a memória imediatamente
    .filter(pl.col('valor') > 5000000) # Filtro para um valor alto para simular menos dados no final
    .group_by('categoria')
    .agg(pl.col('valor').sum().alias('total_filtrado'))
    .sort('total_filtrado', descending=True)
)

print("Plano de execução definido. Executando com .collect()...")
start_time = time.time()
df_lazy_result = query.collect()  # Executa o plano e carrega o resultado
end_time = time.time()
print(f"Lazy evaluation (collect) levou: {end_time - start_time:.2f} segundos")
print("Resultado da lazy evaluation:")
print(df_lazy_result)

# --- Limpeza (opcional) ---
# os.remove('dados_exemplo.csv')
# print("\nArquivo 'dados_exemplo.csv' removido.")
