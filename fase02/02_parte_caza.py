from pathlib import Path

import pandas as pd


DATASET = Path(
    'data/raw/proceseed/nevworld_871785836360798065_20261005_182810.jsonl'
)

OUTPUT_DIR = Path('data/processed')

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


df = pd.read_json(DATASET, lines=True)


def event_table(event_type, columns):

    selected = ['run_id', 'event_index', 'tick', *columns]

    available = [
        column for column in selected
        if column in df.columns
    ]

    table = df.loc[
        df['type'] == event_type,
        available,
    ].copy()

    if not table.empty:
        table['simulation_day'] = table['tick'] // 12000

    return table




cantidad = (df['type'] == 'hunt_completed').sum()

print('Cacerías completadas:', cantidad)




campos_obligatorios = [
    'run_id',
    'event_index',
    'tick', 
    'villager_id',
    'prey_type',
]

if cantidad > 0:
    assert all(
        column in df.columns
        for column in campos_obligatorios
    ), 'Falta algún campo obligatorio para las cacerías'



table = event_table('hunt_completed', [
    'villager_id',
    'prey_type',
])



columnas_de_salida = [
    'run_id',
    'event_index',
    'tick',
    'villager_id',
    'prey_type',
    'simulation_day',
]

table = table.reindex(columns=columnas_de_salida)




assert len(table) == cantidad, \
    'El número de filas no coincide con los eventos del RAW'

assert not table.duplicated(
    ['run_id', 'event_index']
).any(), \
    'Hay eventos de caza duplicados'


if not table.empty:

    assert table[
        campos_obligatorios
    ].notna().all().all(), \
        'Hay campos obligatorios vacíos'

    assert (
        table['simulation_day']
        == table['tick'] // 12000
    ).all(), \
        'simulation_day no coincide con tick // 12000'



output = OUTPUT_DIR / 'hunts.csv'

table.to_csv(output, index=False)


print('Archivo generado:', output)

print('Número de filas:', len(table))
