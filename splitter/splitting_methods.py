import pandas as pd
import numpy as np

def random_from_csv(config):
    """
    Выполняет случайное сэмплирование без повторений и назначает группы 50 на 50, если необходимо.
    
    Параметры:
    - config (dict): Конфигурация, содержащая путь к файлу с группами.
    
    Возвращает:
    - groups (DataFrame): DataFrame с назначенными группами после случайного сэмплирования.
    """
    groups = pd.read_csv(config['groups_path'])
 
    if config['stratification']:
        # Для каждой страты случайно перемешиваем и назначаем группы 50 на 50
        def assign_groups(x):
            x = x.sample(frac=1).reset_index(drop=True)  
            half_len = len(x) // 2 
            x['group'] = ['test' if i < half_len else 'control' for i in range(len(x))] 
            return x
        groups = groups.groupby('strat').apply(assign_groups).reset_index(drop=True)
    else:
        groups = groups.sample(frac=1).reset_index(drop=True)  
        half_len = len(groups) // 2
        groups['group'] = ['test' if i < half_len else 'control' for i in range(len(groups))]

    #groups.sort_values(['strat', 'group', 'restaurant_id']).to_csv(config['groups_path'], index=False)
    return groups

def random_from_population(data, sample_size):
    """
    Изменяет входной DataFrame, добавляя столбец 'group', случайным образом назначая
    n=sample_size ресторанов в тестовую группу и n=sample_size ресторанов в контрольную группу.
    
    Параметры:
    - data (DataFrame): Данные, содержащие уникальные идентификаторы ресторанов.
    - sample_size (int): Количество ресторанов, включаемых в каждую группу.
    
    Возвращает:
    - data (DataFrame): Модифицированный DataFrame с добавленным столбцом 'group'.
    """
    unique_ids = data.restaurant_id.unique()

    if len(unique_ids) < 2 * sample_size:
        raise ValueError("Недостаточно уникальных ресторанов для запрошенного размера выборки.")
    
    selected_ids = np.random.choice(unique_ids, size=2*sample_size, replace=False)
    
    test_ids = selected_ids[:sample_size]
    control_ids = selected_ids[sample_size:]
    
    data.loc[data.restaurant_id.isin(test_ids), 'group'] = 'test'
    data.loc[data.restaurant_id.isin(control_ids), 'group'] = 'control'

    return data[data.restaurant_id.isin(test_ids) | data.restaurant_id.isin(control_ids)]