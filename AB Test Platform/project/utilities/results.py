import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from project.data_processing import ABTest
from project.imports import np, chain, tqdm, pd

def get_results(configurations, common_config, test_group, kiosk_data, kassa_data, cc_data):
    results_df_overall = pd.DataFrame()
    results_df_stats = pd.DataFrame()
    for config in tqdm.tqdm(configurations):
            # Объединяем специфическую конфигурацию с общей конфигурацией
            ab_test_config = {**common_config, **config}

            # Запускаем AB тест
            ab_test = ABTest(ab_test_config, kiosk_data, kassa_data, cc_data)
            results = ab_test.execute(test_group)
            
            # Предполагаем, что results - это вывод из ab_test.execute(test_group)
            AA_mean_test_before = np.mean([res['mean_test_before'] for res in results['AA_results']])
            AA_mean_control_before = np.mean([res['mean_control_before'] for res in results['AA_results']])
            AB_mean_test_after = np.mean([res['mean_test_before'] for res in results['AB_results']])  
            AB_mean_control_after = np.mean([res['mean_control_before'] for res in results['AB_results']])

            # уникальные рестораны
            flattened_restaurant_ids = list(chain.from_iterable(results['AA_test_pass_list']))
            unique_restaurant_count = len(set(flattened_restaurant_ids))  

            new_row_overall = {
                'Метрика': ab_test_config['aggregator'],
                'Тип': ab_test_config['aggregation_type'],
                'Канал': ab_test_config['parameter'],
                'ДО test-группы': round(AA_mean_test_before, 4),
                'ДО control-группы': round(AA_mean_control_before, 4),
                'ПОСЛЕ test-группы': round(AB_mean_test_after, 4),
                'ПОСЛЕ control-группы': round(AB_mean_control_after, 4),
                'Прирост test-группы, %': round((AB_mean_test_after / AA_mean_test_before - 1) * 100, 2),
                'Прирост control-группы, %': round((AB_mean_control_after / AA_mean_control_before - 1) * 100, 2),
                'p_value': np.mean([res['p_value'] for res in results['AB_results']]),
            }
            new_row_stats = {
                'Метрика': ab_test_config['aggregator'],
                'Тест': ab_test_config['test'],
                'AB p_value': np.mean([res['p_value'] for res in results['AB_results']]),
                'AB p_value std': 1.96*np.std([res['p_value'] for res in results['AB_results']]) / np.sqrt(len(test_group)),
                'AA p_value': np.mean([res['p_value'] for res in results['AA_results']]),
                'bp_count': len(results['AA_test_pass_list']),
                'unique_ids': round(unique_restaurant_count / len((flattened_restaurant_ids)), 2)
            }
            # Добавляем новую строку в DataFrame
            new_row_df_overall = pd.DataFrame([new_row_overall], index=[len(results_df_overall)])
            results_df_overall = pd.concat([results_df_overall, new_row_df_overall])
            new_row_stats = pd.DataFrame([new_row_stats], index=[len(results_df_stats)])
            results_df_stats = pd.concat([results_df_stats, new_row_stats])

    return results_df_overall, results_df_stats, \
        results['data_histogram_path'], results['test_data_histogram_path'], results['control_data_histogram_path']
