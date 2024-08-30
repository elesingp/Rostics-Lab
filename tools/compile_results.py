from ab_test import ABTest
from aa_test import AATest
from .get_restaurant_aggregates import get_restraunts_aggregates_df
from common_paths import *

import pandas as pd
import tqdm

def rename_metric(metric_name):
    naming_df = pd.read_csv(naming_conventions_path)

    if isinstance(metric_name, tuple):
        metric_name = ', '.join(map(str, metric_name))
        
    if metric_name in naming_df['Техническое название'].values:
        naming_dict = pd.Series(naming_df['Правильное название'].values, index=naming_df['Техническое название']).to_dict()
        metric_name = naming_dict.get(metric_name, metric_name)

    return metric_name


def compile_results_ab(configurations, data):
    """
    Собирает результаты A/B тестирования и нужные пути из предоставленных данных.
    Проходимся по каждой конфигурации.
    Каждая конфигурация - это метрика, заданная словарем в файле config.py

    Параметры:
        configurations (list): Список конфигураций для каждого теста.
        common_config (dict): Общая конфигурация, применяемая ко всем тестам.
        kiosk_data (DataFrame): Данные киосков.
        kassa_data (DataFrame): Данные касс.
        cc_data (DataFrame): Данные C&C.
        test_group (list): Список ресторанов в тестовой группе. - optional

    Возвращает:
        tuple: 
            Содержит DataFrame общих результатов - overall_results:
                1) Метрика: значение поля 'aggregator' в конфиге метрики.
                        Пример: 'aggregator': 'orders'
                        Замечание: такой столбец должен существовать таблице с данными для A/B теста.
                2) Тип: значение поля 'aggregation_type' в конфиге метрики. 
                   Может быть mean или sum, в зависимости от того, как выглядит таблица с данными для A/B теста.
                3) Канал: значение поля 'parameter' в конфиге метрики.
                   Является дополнительным условием для метрики. Заводиться вручную. 
                   Обязательно должен быть написан на синтаксисе python
                        Пример: 'parameter': 'orders > 10', 'parameter': 'channel == "kiosk"'
                4) ДО test-группы: значение метрики для тест-группы до начала теста.
                   Начало теста указывается в common_config теста в формате YYYY-MM-DD.
                        Пример: 'start_date': '2023-12-16'
                        Замечание: день теста не включается в результаты A/B тестирования.
                5) ДО control-группы: значение метрики для control-группы до начала теста.
                6) ПОСЛЕ test-группы: значение метрики для тест-группы после начала теста.
                7) ПОСЛЕ control-группы: значение метрики для control-группы после начала теста.
                8) Прирост test-группы, %: процент пртрост отношения средних значений test-групп,
                   посчитанный по формуле:
                        (ПОСЛЕ test-группы / ДО test-группы - 1) * 100
                9) Прирост control-группы, %: процент пртрост отношения средних значений control-групп,
                   посчитанный по формуле:
                        (ПОСЛЕ control-группы / ДО control-группы - 1) * 100
                10) p_value: среднее значение p-value из словаря results.
                Сравнивается тестовая и контрольная выборка после начала теста.

            DataFrame статистических результатов - stat_results:
                1) Метрика: значение поля 'aggregator' в конфиге метрики.
                        Пример: 'aggregator': 'orders'
                        Замечание: такой столбец должен существовать таблице с данными для A/B теста.
                2) Тест: значение поля 'method' в конфиге метрики. 
                   Обозначает, какой статисический тест использовался.
                3) AB p_value: среднее значение p-value из словаря results.
                4) AB p_value std: 95% доверительный интервал p-value из словаря results.
                   Вычисляется по формуле:
                        1.96 * std(p_value) / sqrt(len(test_group)),
                        Замечание: если метод не подразумевает усреднение p_value, то значене будет 0.
                5) AA p_value: среднее значение p-value АА теста из словаря results.
                   Должен быть больше 0.05.
        histogram_path: Путь к файлу с гистограммой распределения метрики генеральной совокупности.
        test_histogram_path: Путь к файлу с гистограммой распределения метрики тестовой группы.
        control_histogram_path: Путь к файлу с гистограммой распределения метрики контрольной группы.
        plot_path: Путь к файлу с графиком динамики метрики тестовой и контрольной групп.
            Замечание: интервал задается в common_config через переменные 'data_collect_start_date' и 'data_collect_end_date'.
    """
    
    # Создание пустых DataFrame для общих результатов A/B теста.
    overall_results = pd.DataFrame()
    detailed_results = pd.DataFrame()

    for config in tqdm.tqdm(configurations['configurations_ab']):
        
        # Объединение конфигураций для удобства 
        config = {**configurations['common_config_ab'], **config}
        print(config)
        
        data_copy = data.copy()
        # Инициализация класса аб-тестирования и выполнение A/B теста
        
        ab_test = ABTest(config)
        results = ab_test.execute(data_copy)

        # Создание новых строк для DataFrame
        new_row_overall = {
            'exp_id': config['exp_id'],
            'metric_id': config['metric_id'],
            'Метрика': rename_metric(config['aggregator']),
            'Тип': config['aggregation_type'],
            'Канал': config['parameter'],
            'До test': round(results['overall_results_aa']['mean_test'], 4),
            'До control': round(results['overall_results_aa']['mean_control'], 4),
            'После test': round(results['overall_results_ab']['mean_test'], 4),
            'После control': round(results['overall_results_ab']['mean_control'], 4),
            'Количество измерений': results['overall_results_ab']['sample_count'], 
            'Разница': results['overall_results_ab']['mean_test'] - results['overall_results_ab']['mean_control'],
            'Разница %': 100 * (results['overall_results_ab']['mean_test'] - results['overall_results_ab']['mean_control']) / results['overall_results_aa']['mean_control'] - ((results['overall_results_aa']['mean_test'] - results['overall_results_aa']['mean_control']) / results['overall_results_aa']['mean_control']),
            'MDE': config['MDE'],
            'p_value': round(results['stat_results_ab']['pvalue'], 3),
            'flag': -1
        }
        new_row_detailed = {
            'exp_id': config['exp_id'],
            'metric_id': config['metric_id'],
            'Метрика': config['aggregator'],
            'Преобразование': config['transform'],
            'Тест': config['test'],
            'Метод': config['method'],
            'Сплитование': config['split_method'],
            'AA pvalue': results['stat_results_aa']['pvalue'],
            'visualization_names': results['visualization_names'],
            'aggregate_path': get_restraunts_aggregates_df(results['aggregate_dict_copy'], config['aggregator'], config['exp_id'], config['metric_id']),
        }

        overall_results = pd.concat([overall_results, pd.DataFrame([new_row_overall])], ignore_index=True)
        detailed_results = pd.concat([detailed_results, pd.DataFrame([new_row_detailed])], ignore_index=True)
    
    return overall_results, detailed_results

def compile_results_aa(configurations, data):

    overall_results = pd.DataFrame()
    detailed_results = pd.DataFrame()

    for config in tqdm.tqdm(configurations['configurations_aa']):
        config = {**configurations['common_config_aa'], **config}

        data_copy = data.copy()
        
        aa_test = AATest(config)
        results = aa_test.execute(data_copy)
        stat_results = results['results_df']
        for index, row in stat_results.iterrows():
            new_row_overall = {
                'exp_id': config['exp_id'],
                'metric_id': config['metric_id'],
                'Метрика': config['aggregator'],
                'Тип': config['aggregation_type'],
                'Канал': config['parameter'],
                'method': config['method'], 
                'test': config['test'],  
                'mde': row['mde'], 
                'first_type_errors': row['first_type_errors'], 
                'second_type_errors': row['second_type_errors']
            }
            new_row_detailed = {
                'visualization_names': row['visualization_name'],
            }
            overall_results = pd.concat([overall_results, pd.DataFrame([new_row_overall])], ignore_index=True)
            detailed_results = pd.concat([detailed_results, pd.DataFrame([new_row_detailed])], ignore_index=True)
    
    return overall_results, detailed_results