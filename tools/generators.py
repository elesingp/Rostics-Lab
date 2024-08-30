import pandas as pd
from common_paths import *
import os

def generate_unique_exp_id():
    df_experiments = pd.read_csv(experiments_path)
    if df_experiments.empty:
        return 0
    else:
        return df_experiments['exp_id'].max() + 1
    
def generate_unique_path(exp_id, metric_id, visualization_type, aggregator_name, unique_name, extension='.png'):
        """
        Генерирует уникальный путь к файлу на основе базового пути, названия агрегатора, уникального идентификатора и расширения файла.

        Параметры:
        - base_path (str): Базовый путь к файлу.
        - aggregator_name (str): Название агрегатора.
        - unique_id (str): Уникальный идентификатор.
        - extension (str): Расширение файла.

        Возвращает:
        - str: Уникальный путь к файлу.
        """
        # Убедимся, что расширение файла начинается с точки
        if not extension.startswith('.'):
            extension = '.' + extension
        # Заменяем расширение файла на уникальный идентификатор и название агрегатора, затем добавляем расширение
        filename = f'{visualization_type}_{exp_id}_{metric_id}_{aggregator_name}_{unique_name}{extension}'
        unique_path = os.path.join(base_vizualization_path, filename)
        return unique_path, filename