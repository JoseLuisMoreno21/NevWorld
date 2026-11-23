from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


HUNTS_PATH = Path('data/processed/hunts.csv')
CHARTS_DIR = Path('reports/charts')
CHART_PATH = CHARTS_DIR / '05_hunts_by_prey.png'

if not HUNTS_PATH.exists():
    raise FileNotFoundError(
        f'No existe {HUNTS_PATH}. Genera primero la tabla en la actividad 02.'
    )

hunts = pd.read_csv(HUNTS_PATH)

if 'prey_type' not in hunts.columns:
    raise ValueError('hunts.csv no contiene la columna obligatoria prey_type.')


if hunts.empty:
    print('AVISO: no hay cacerías completadas registradas; no se generará el gráfico.')
    if CHART_PATH.exists():
        print(
            f'AVISO: {CHART_PATH} ya existía de una ejecución anterior; '
            'no corresponde a esta partida sin cacerías.'
        )
else:
    # No permitir que value_counts() oculte cacerías sin una presa informada.
    prey_type = hunts['prey_type'].astype('string')
    missing_prey = hunts['prey_type'].isna() | prey_type.str.strip().eq('')
    if missing_prey.any():
        raise ValueError(
            'Cada cacería debe tener una presa informada en prey_type; '
            f'hay {int(missing_prey.sum())} fila(s) sin presa.'
        )

    # Reutiliza la validación de claves de evento de la actividad 03.
    if {'run_id', 'event_index'}.issubset(hunts.columns):
        assert not hunts.duplicated(['run_id', 'event_index']).any(), (
            'Hay cacerías duplicadas con la misma clave (run_id, event_index).'
        )

    counts = hunts['prey_type'].value_counts()
    assert counts.sum() == len(hunts), (
        'La suma de cacerías por presa debe coincidir con el total de filas.'
    )

    print('Cacerías completadas registradas por tipo de presa:')
    print(counts)
    print('Total de cacerías:', int(counts.sum()))

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4))
    counts.plot.bar(color='steelblue')
    plt.title('Cacerías completadas registradas por tipo de presa')
    plt.xlabel('Tipo de presa')
    plt.ylabel('Número de cacerías completadas')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig(CHART_PATH)
    plt.close()

    print('Gráfico guardado en:', CHART_PATH)
