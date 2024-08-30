import pandas as pd
import numpy as np
from datetime import datetime

def prepare_table_for_ab_test_1(data, channel, start_date, end_date):
    """
    Подготавливает данные для A/B теста 1, выполняя фильтрацию, переименование столбцов и удаление ненужных столбцов.
    
    Параметры:
    - data (DataFrame): Исходные данные.
    - channel (str): Канал продаж (например, 'kassa', 'cc', 'kiosk').
    - start_date (str): Начальная дата диапазона фильтрации.
    - end_date (str): Конечная дата диапазона фильтрации.
    
    Возвращает:
    - DataFrame: Обработанные данные.
    """
    data = data.copy()

    if channel in ['kassa', 'cc']:
        data = data.drop(['Franchisee Name', 'City', 'Name', 'Facility',
                          'AGC (Net)', 'Rating', 'Dish Quantity', 'Period',
                          'DoW', 'RestPick', 'Rest excl'], axis=1)
        data = data.rename(columns={'Code': 'restraunt_id',
                                    'Date': 'event_date', 'Net Sales': 'revenue',
                                    'Checs Qnt': 'order_success_count'})
    elif channel == 'kiosk':
        data['event_date'] = data['event_date'].apply(lambda x: datetime.strptime(str(x), "%Y%m%d").strftime("%Y-%m-%d"))
        data = data[['restraunt_id',  'event_date', 'revenue', 'order_success_count']]

    data['channel'] = channel
    data['event_date'] = pd.to_datetime(data['event_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    data['day_of_week'] = pd.to_datetime(data['event_date'], errors='coerce').dt.day_name()
    data = data[(data['event_date'] > start_date) & (data['event_date'] < end_date)]

    return data

def prepare_table_for_ab_test_2(data, start_date, end_date):
    """
    Подготавливает данные для A/B теста 2, выполняя фильтрацию и форматирование даты ТОЛЬКО данных по киоску.
    Данные по кассе и C&C не преобразовываются.
    
    Параметры:
    - data (DataFrame): Исходные данные, удовлетворяющие формату:
        'event_date' | 'restraunt_id' | 'feature_1' | 'feature_2' | 'feature_3' | ... | 'feature_n',
            где:
            'event_date' - дата расчета метрики в формате YYYYMMDD,
            'restraunt_id' - ID ресторана(8 цифр) с типом данных ???,
            'feature_i' - значение целевой метрики с типом данных float.
    - channel (str): Канал продаж (например, 'kiosk').
    - start_date (str): Начальная дата диапазона фильтрации.
    - end_date (str): Конечная дата диапазона фильтрации.
    
    1) Меняет формат дат с YYYYMMDD на формат '%Y-%m-%d'.
    2) Создает столбец channel с названием канала продаж.
    3) Создает столбец day_of_week с названием дня недели.
    4) Обрезает данные по диапазону начала и конца теста.
    
    Возвращает:
    - DataFrame: Обработанные данные.
    """
    data = data.copy()
    channel = 'kiosk'
    if channel in ['kassa', 'cc']:
        return data
    elif channel == 'kiosk':
        data['date'] = data['date'].apply(lambda x: datetime.strptime(str(x), "%Y%m%d").strftime("%Y-%m-%d"))
        data['channel'] = channel
        data['date'] = pd.to_datetime(data['date'], errors='coerce').dt.strftime('%Y-%m-%d')
        data['day_of_week'] = pd.to_datetime(data['date'], errors='coerce').dt.day_name()
        data['date'] = pd.to_datetime(data['date'])
        start_date_ts = pd.to_datetime(start_date)
        end_date_ts = pd.to_datetime(end_date)
        data = data[(data['date'] >= start_date_ts) & (data['date'] <= end_date_ts)]
        return data
    
def prepare_table_for_ab_test_3(data, start_date, end_date):
    """
    Подготавливает данные для A/B теста 3, выполняя фильтрацию и форматирование даты ТОЛЬКО данных по киоску.
    Данные по кассе и C&C не преобразовываются.
    
    Возвращает:
    - DataFrame: Обработанные данные.
    """
    data = data.copy()
    data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
    return data

class PrepareData:
    @staticmethod
    def get(data, ab_test_name, start_date, end_date):
        """
        Выбирает подходящую функцию подготовки данных в зависимости от названия A/B теста.
        
        Параметры:
        - data (DataFrame): Исходные данные.
        - channel (str): Канал продаж.
        - ab_test_name (str): Название A/B теста.
            Задается в common_config для всех метрик данного теста.
        - start_date (str): Начальная дата диапазона фильтрации.
        - end_date (str): Конечная дата диапазона фильтрации.
        
        Возвращает:
        - DataFrame: Обработанные данные.
        """
        channel = 'kiosk'
        if ab_test_name in ['ab_test_1']:
            return prepare_table_for_ab_test_1(data, channel, start_date, end_date)
        if ab_test_name in ['ab_test_2']:
            return prepare_table_for_ab_test_2(data, start_date, end_date)
        if ab_test_name in ['ab_test_3']:
            return prepare_table_for_ab_test_3(data, start_date, end_date)
        return data

# Data Concatenation
class Concatenation:
    @staticmethod
    def concat_data(a, b):
        """
        Объединяет два DataFrame в один.
        
        Параметры:
        - a (DataFrame): Первый набор данных.
        - b (DataFrame): Второй набор
        """
        return pd.concat([a, b], ignore_index=True)