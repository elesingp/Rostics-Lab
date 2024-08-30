# File Data Loading
import pandas as pd
import numpy as np
import json
from clickhouse_connect import get_client
import unittest
from datetime import datetime, timedelta
import tqdm
import scipy

from common_paths import *
class Uploader:
    """
    Класс для загрузки данных различных форматов.
    """
    @staticmethod
    def upload_from_file(path, format):
        """
        Загружает данные из файла в DataFrame.

        В зависимости от формата файла использует соответствующий метод pandas для загрузки данных.
        Для формата 'excel' используется pd.read_excel, для 'csv' - pd.read_csv.

        Parameters:
            path (str): Путь к файлу для загрузки данных.
            format (str): Формат файла ('excel' или 'csv').

        Returns:
            pandas.DataFrame: Данные, загруженные из файла.
        """
        if format == 'excel':
            return pd.read_excel(path)
        if format == 'csv':
            return pd.read_csv(path, sep=',')
    
    @staticmethod
    def generate_dynamic_features_data(start_date='2023-12-15', end_date='2023-12-15', num_restaurants=500, num_sessions_per_restaurant=10, features_config=None):
        """
        Генерирует данные для списка ресторанов с динамическими фичами, основанными на различных распределениях, включая сессии.

        Parameters:
            start_date (str): Строковое представление начальной даты в формате 'YYYY-MM-DD'.
            end_date (str): Строковое представление конечной даты в формате 'YYYY-MM-DD'.
            num_restaurants (int): Количество ресторанов для генерации данных.
            num_sessions_per_restaurant (int): Количество сессий для генерации для каждого ресторана в каждую дату.
            features_config (dict): Словарь конфигураций для генерации фичей. Ключ - название фичи, значение - словарь с параметрами распределения и типом распределения.

        Returns:
            pandas.DataFrame: DataFrame с сгенерированными данными.
        """
        features_config = {
            'order_value': {'distribution': 'normal', 'mean': 500, 'std': 100},
            'is_success_order1': {'distribution': 'binomial', 'n': 1, 'p': 0.5},
            'is_success_order2': {'distribution': 'binomial', 'n': 1, 'p': 0.5},
            'views': {'distribution': 'lognormal', 'mean': 1, 'std': 1},
            'uniform_discount': {'distribution': 'uniform', 'low': 5, 'high': 20},
            'exponential_wait_time': {'distribution': 'exponential', 'scale': 1/1.5},  # Lambda = 1.5
            'ctr': {'distribution': 'beta', 'success_rate': 0.2, 'beta': 100},
            'clicks': {'distribution': 'lognormal*beta', 'mean': 1, 'std': 1, 'success_rate': 0.2, 'beta': 1000},  
        }

        np.random.seed(80)
        # Генерация списка дат
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        date_range = [start_date_obj + timedelta(days=x) for x in range((end_date_obj - start_date_obj).days + 1)]

        # Генерация данных
        data = []
        for date in date_range:
            for restaurant_id in range(1, num_restaurants + 1):
                for session_id in range(1, num_sessions_per_restaurant + 1):
                    row = {'date': date, 'restaurant_id': restaurant_id, 'session_id': session_id}
                    for feature_name, config in features_config.items():
                        if config['distribution'] == 'normal':
                            if restaurant_id <= num_restaurants/2:  
                                row[feature_name] = np.random.normal(config['mean'], config['std'])
                            else:
                                row[feature_name] = np.random.normal(config['mean'], config['std'])
                        elif config['distribution'] == 'binomial':
                            row[feature_name] = np.random.binomial(config['n'], config['p'])
                        elif config['distribution'] == 'lognormal':
                            row[feature_name] = np.random.lognormal(config['mean'], config['std'])
                        elif config['distribution'] == 'uniform':
                            row[feature_name] = np.random.uniform(config['low'], config['high'])
                        elif config['distribution'] == 'exponential':
                            row[feature_name] = np.random.exponential(config['scale'])
                        elif config['distribution'] == 'beta':  
                            alpha = config['success_rate'] * config['beta'] / (1 - config['success_rate'])
                            row[feature_name] = np.random.beta(alpha, config['beta'])
                        elif config['distribution'] == 'lognormal*beta':  
                            alpha = config['success_rate'] * config['beta'] / (1 - config['success_rate'])
                            row[feature_name] = np.random.lognormal(config['mean'], config['std'])*np.random.beta(alpha, config['beta'])
                    data.append(row)
                    
        # Количество ресторанов в каждой страте
        restaurants_per_strat = num_restaurants / 2
        print(num_restaurants)
        # Создание DataFrame
        df = pd.DataFrame({
            'restaurant_id': np.arange(1, int(restaurants_per_strat * 2) + 1),
            'strat': np.repeat([1, 2], restaurants_per_strat),
            'group': np.tile(np.repeat(['control', 'test'], restaurants_per_strat // 2), 2)
        })

        print(df.head()) 
        df.to_csv(stratification_groups_path, index=False)  
        return pd.DataFrame(data)
    
    @staticmethod
    def upload_from_clickhouse(config, sql_queries):
        """
        Динамически составляет и выполняет SQL-запрос к ClickHouse, используя параметры из конфига и словарь SQL запросов.

        Parameters:
            config (dict): Конфигурация для составления SQL-запроса.
            sql_queries (dict): Словарь с SQL запросами для каждой метрики.

        Returns:
            pandas.DataFrame: Данные, загруженные из ClickHouse.
        """
        with open('C:\\ROSTICS-LAB\\project\\tools\\clickhouse_config.json', 'r') as config_file:
            clickhouse_config = json.load(config_file)
        
        metrics = config['aggregator'].split('/')  # Разбиваем агрегатор на отдельные метрики, если указано несколько
        queries_results = []

        for metric in metrics:
            if metric in sql_queries:
                # Используем предопределенный SQL запрос для метрики
                query = sql_queries[metric].format(start_date=config['data_collect_start_date'], end_date=config['data_collect_end_date'])
            else:
                # Запасной вариант, если для метрики не определен SQL запрос
                query = f"""SELECT toDate(event_datetime) as date, restaurant_id, kiosk_session_id as session_id, {metric}
                            FROM abtest_table
                            WHERE restaurant_id != 0 AND toDate(event_datetime) >= '{config['data_collect_start_date']}' AND toDate(event_datetime) <= '{config['data_collect_end_date']}'
                            ORDER BY date"""

            max_attempts = 3
            attempts = 0
            query_result = None

            while attempts < max_attempts and query_result is None:
                try:
                    client = get_client(**clickhouse_config)
                    query_result = client.query_df(query)
                    queries_results.append(query_result)
                except Exception as e:
                    print(f"Ошибка при выполнении запроса для метрики {metric}: {e}. Попытка {attempts + 1} из {max_attempts}.")
                    attempts += 1

        if queries_results:
            # Объединяем результаты запросов для разных метрик, если это необходимо
            final_df = pd.concat(queries_results, axis=1)
            return final_df
        else:
            raise Exception("Не удалось выполнить ни одного запроса.")
    

def get_quantitative_features(config):
    """
    Агрегирует переданный DataFrame по 'restaurant_id', вычисляя среднее значение и стандартное отклонение
    для каждой количественной колонки, исключая 'restaurant_id'.

    Параметры:
        df (pandas.DataFrame): DataFrame для агрегации.

    Возвращает:
        pandas.DataFrame: Агрегированный DataFrame с средним и стандартным отклонением для каждой количественной колонки.
    """
    
    start_date = config['common_config_clustering']['data_collect_start_date']
    end_date = config['common_config_clustering']['data_collect_end_date']

    query = f"""SELECT 
                    toDate(event_datetime) as date,
                    restaurant_id,
                    kiosk_session_id as session_id,
                    order_value,
                    product_qnt,
                    used_points_qnt
                FROM abtest_table 
                WHERE restaurant_id != 0 
                AND toDate(event_datetime) >= '{start_date}'
                AND toDate(event_datetime) <= '{end_date}'
                ORDER BY 'date' """

    print(query)
            
    df = Uploader.upload_from_clickhouse(query)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'restaurant_id' in numeric_cols:
        numeric_cols.remove('restaurant_id')  

    agg_funcs = {col: ['mean', 'std'] for col in numeric_cols}

    quantitative_features_table = df.groupby('restaurant_id').agg(agg_funcs).reset_index()

    quantitative_features_table.columns = ['_'.join(col).strip() if col[1] else col[0] for col in quantitative_features_table.columns.values]
    
    return quantitative_features_table
