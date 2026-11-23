from pathlib import Path

import pandas as pd

HUNTS_PATH = Path('data/processed/hunts.csv')
RESOURCES_PATH = Path('data/processed/resources.csv')
REPORTS_DIR = Path('reports')
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

if not HUNTS_PATH.exists():
    raise FileNotFoundError(
        f'No existe {HUNTS_PATH}. Termina primero la actividad 02.'
    )

if not RESOURCES_PATH.exists():
    raise FileNotFoundError(
        f'No existe {RESOURCES_PATH}. Genera resources.csv en la actividad correspondiente.'
    )

hunts = pd.read_csv(HUNTS_PATH)
resources = pd.read_csv(RESOURCES_PATH)

columnas_hunts = [
    'run_id', 'event_index', 'tick', 'villager_id', 'prey_type',
    'simulation_day',
]
columnas_resources = [
    'run_id', 'event_index', 'resource_type', 'amount_delta',
]

for columna in columnas_hunts:
    assert columna in hunts.columns, f'Falta la columna {columna} en hunts.csv'

for columna in columnas_resources:
    assert columna in resources.columns, f'Falta la columna {columna} en resources.csv'

assert not hunts.duplicated(['run_id', 'event_index']).any(), \
    'Hay claves (run_id, event_index) duplicadas en hunts.csv'
assert not resources.duplicated(['run_id', 'event_index']).any(), \
    'Hay claves (run_id, event_index) duplicadas en resources.csv'

partidas_hunts = set(hunts['run_id'].dropna().unique())
partidas_resources = set(resources['run_id'].dropna().unique())
assert len(partidas_hunts) <= 1, 'hunts.csv contiene más de una partida'
assert len(partidas_resources) <= 1, 'resources.csv contiene más de una partida'
if partidas_hunts and partidas_resources:
    assert partidas_hunts == partidas_resources, \
        'hunts.csv y resources.csv no corresponden a la misma partida'

assert hunts[['run_id', 'event_index', 'tick', 'villager_id', 'prey_type', 'simulation_day']].notna().all().all(), \
    'Hay valores ausentes en campos usados de hunts.csv'
assert resources[['run_id', 'event_index', 'resource_type', 'amount_delta']].notna().all().all(), \
    'Hay valores ausentes en campos usados de resources.csv'

total_cacerias = len(hunts)
print('TOTAL DE CACERÍAS COMPLETADAS:', total_cacerias)

if hunts.empty:
    print('No hay cacerías completadas registradas.')
else:
    recuento_presas = hunts['prey_type'].value_counts()
    porcentajes_presas = (
        hunts['prey_type'].value_counts(normalize=True) * 100
    ).round(1)
    recuento_dias = hunts['simulation_day'].value_counts().sort_index()

    print('\nCACERÍAS POR TIPO DE PRESA (de mayor a menor):')
    print(recuento_presas)
    print('\nPORCENTAJE POR TIPO DE PRESA (%):')
    print(porcentajes_presas)
    print('\nCACERÍAS POR DÍA (orden cronológico):')
    print(recuento_dias)

    assert recuento_presas.sum() == total_cacerias, \
        'Los recuentos por presa no coinciden con el total'
    assert recuento_dias.sum() == total_cacerias, \
        'Los recuentos por día no coinciden con el total'

    suma_porcentajes = (hunts['prey_type'].value_counts(normalize=True) * 100).sum()
    assert abs(suma_porcentajes - 100) < 0.000001, \
        'Los porcentajes sin redondear no suman aproximadamente 100'

food = resources[resources['resource_type'] == 'food']
numero_cambios_comida = len(food)

if food.empty:
    print('\nAVISO: no hay eventos de cambio de comida registrados.')
    incrementos_comida = 0
    reducciones_comida = 0
    balance_comida = 0
else:
    incrementos_comida = food.loc[food['amount_delta'] > 0, 'amount_delta'].sum()
    reducciones_comida = food.loc[food['amount_delta'] < 0, 'amount_delta'].abs().sum()
    balance_comida = food['amount_delta'].sum()

print('\nCAMBIOS DE COMIDA:')
print('Eventos de cambio de comida:', numero_cambios_comida)
print('Incrementos registrados:', incrementos_comida)
print('Reducciones registradas (magnitud positiva):', reducciones_comida)
print('Balance neto registrado:', balance_comida)

assert abs((incrementos_comida - reducciones_comida) - balance_comida) < 0.000001, \
    'Incrementos menos reducciones no coincide con el balance neto'

resumen = pd.DataFrame([
    {'metric': 'hunt_events', 'value': total_cacerias},
    {'metric': 'food_change_events', 'value': numero_cambios_comida},
    {'metric': 'food_gains', 'value': incrementos_comida},
    {'metric': 'food_reductions', 'value': reducciones_comida},
    {'metric': 'food_net_change', 'value': balance_comida},
])

output_path = REPORTS_DIR / 'hunting_summary.csv'
resumen.to_csv(output_path, index=False)
print('\nComprobaciones superadas.')
print('Informe guardado en:', output_path)
