from pathlib import Path

import duckdb
import pandas as pd


HUNTS_CSV_PATH = Path('data/processed/hunts.csv')
PARQUET_DIR = Path('data/processed/parquet')
PARQUET_PATH = PARQUET_DIR / 'hunts.parquet'
REPORTS_DIR = Path('reports')
SUMMARY_PATH = REPORTS_DIR / 'hunts_by_prey_sql.csv'

if not HUNTS_CSV_PATH.exists():
    raise FileNotFoundError(
        f'No existe {HUNTS_CSV_PATH}. Genera primero hunts.csv en la actividad 02.'
    )

hunts = pd.read_csv(HUNTS_CSV_PATH)

if 'prey_type' not in hunts.columns:
    raise ValueError('hunts.csv no contiene la columna obligatoria prey_type.')

prey_type = hunts['prey_type'].astype('string')
missing_prey = hunts['prey_type'].isna() | prey_type.str.strip().eq('')
if missing_prey.any():
    raise ValueError(
        'Cada cacería debe tener una presa informada en prey_type; '
        f'hay {int(missing_prey.sum())} fila(s) sin presa.'
    )

PARQUET_DIR.mkdir(parents=True, exist_ok=True)
hunts.to_parquet(PARQUET_PATH, engine='pyarrow', index=False)

print('Tamaño del CSV (bytes):', HUNTS_CSV_PATH.stat().st_size)
print('Tamaño del Parquet (bytes):', PARQUET_PATH.stat().st_size)

if hunts.empty:
    print('AVISO: hunts.csv solo tiene cabecera; no hay cacerías para contar.')

hunt_query = """
SELECT
    prey_type,
    COUNT(*) AS hunt_count
FROM read_parquet('data/processed/parquet/hunts.parquet')
GROUP BY prey_type
ORDER BY hunt_count DESC
"""

connection = duckdb.connect()
try:
    sql_counts = connection.execute(hunt_query).fetchdf()

    if hunts.empty:
        sql_counts = sql_counts.reindex(columns=['prey_type', 'hunt_count'])

    print('\nRecuento SQL por tipo de presa:')
    print(sql_counts)

    total_sql = int(sql_counts['hunt_count'].sum())
    if total_sql != len(hunts):
        raise AssertionError(
            f'La suma SQL ({total_sql}) no coincide con las filas del CSV ({len(hunts)}).'
        )
    print('Suma de hunt_count:', total_sql)
    print('Filas del CSV:', len(hunts))

    pandas_counts = {
        str(prey): int(count)
        for prey, count in hunts['prey_type'].value_counts().items()
    }
    duckdb_counts = {
        str(row.prey_type): int(row.hunt_count)
        for row in sql_counts.itertuples(index=False)
    }
    if pandas_counts != duckdb_counts:
        raise AssertionError(
            'Los recuentos SQL no coinciden con value_counts() de pandas '
            '(actividades 03 y 04).'
        )
    print('Comparación con pandas (actividades 03 y 04): coincide.')

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    sql_counts.to_csv(SUMMARY_PATH, index=False)
    print('Resumen guardado en:', SUMMARY_PATH)
finally:
    connection.close()
