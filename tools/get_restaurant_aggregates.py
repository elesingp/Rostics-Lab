import pandas as pd
import os
from common_paths import *

def get_restraunts_aggregates_df(aggregate_dict, metric_name, exp_id, metric_id):
    """
    Агрегирует данные по ресторанам из словаря aggregate_dict, учитывая тестовую и контрольную группы,
    и сохраняет результат в CSV-файл с расширенной структурой.
    
    Параметры:
        aggregate_dict (dict): Словарь с DataFrame'ами, включая данные до и после для тестовой и контрольной групп.
        metric_name (str): Название метрики.
        exp_id (str): Идентификатор эксперимента.
        metric_id (str): Идентификатор метрики.
    
    Возвращает:
        Путь к сохраненному CSV файлу.
    """
    # Объединяем данные из разных частей словаря в один DataFrame
    if isinstance(metric_name, tuple):
        metric = metric_name[2]
    else:
        metric = metric_name

    data_frames = []
    print(aggregate_dict)
    for key, df in aggregate_dict.items():
        # Предполагается, что каждый DataFrame уже содержит колонку 'period' с метками 'before' или 'after'
        data_frames.append(df)
    full_data = pd.concat(data_frames)
    
    # Разделяем данные на 'before' и 'after', агрегируем их по 'restaurant_id', 'group'
    before_data = full_data[full_data['status'] == 'before'].groupby(['restaurant_id', 'group']).agg({metric: 'mean'}).rename(columns={metric: 'Метрика До'}).reset_index()
    after_data = full_data[full_data['status'] == 'after'].groupby(['restaurant_id', 'group']).agg({metric: 'mean'}).rename(columns={metric: 'Метрика После'}).reset_index()
    
    # Объединяем данные 'before' и 'after'
    merged_data = pd.merge(before_data, after_data, on=['restaurant_id', 'group'])
    
    # Рассчитываем абсолютное и процентное изменение
    merged_data['Изменение'] = round(merged_data['Метрика После'] - merged_data['Метрика До'], 2)
    merged_data['Изменение, %'] = round((merged_data['Изменение'] / merged_data['Метрика До']) * 100, 2)
    merged_data['Метрика После'] = round(merged_data['Метрика После'], 2)
    merged_data['Метрика До'] = round(merged_data['Метрика До'], 2)
    
    # Составляем уникальное имя файла на основе exp_id и metric_id
    filename = f"restaurant_aggregates_{exp_id}_{metric_id}.csv"
    path = os.path.join(base_restaurant_path, filename)
    
    # Сохраняем агрегированные данные в CSV
    merged_data.to_csv(path, index=False)
    
    return path