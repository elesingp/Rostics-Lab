import pandas as pd
import numpy as np

from .splitting_methods import random_from_csv, random_from_population

# Data Splitting
class Splitter:
    def __init__(self, config):
        """
        Инициализирует объект класса с данными и конфигурацией.
        
        Параметры:
        - config (dict): Конфигурация исследуемой метрики.
        """
        self.config = config
    def __split_before_after(self, data):
        """
        Разделяет данные на периоды до, во время и после начала эксперимента.
        
        Параметры:
        - data (DataFrame): Данные для разделения.
        - start_date (str): Дата начала экспериммента
        
        Возвращает: 
            Создается новая колоника 'status', содержащая значения 'Before', 'After' и 'Start'
        """
        self.config['start_date'] = pd.to_datetime(self.config['start_date'])
        data['status'] = data['date'].apply(lambda x: 'after' if x > self.config['start_date'] else 'before' if x < self.config['start_date'] else 'start')
        return data
    
    def __split_test_control(self, data):
        """
        Разделяет данные на тестовую и контрольную группы.
        
        Параметры:
        - data (DataFrame): Данные для разделения.
        
        Возвращает:
        - test_data (DataFrame): Данные тестовой группы.
        - control_data (DataFrame): Данные контрольной группы.
        """
        
        if self.config['split_method'] == 'from_csv':
            groups = pd.read_csv(self.config['groups_path'])
            data = data.merge(groups, on='restaurant_id', how='left').dropna()
        
        if self.config['split_method'] == 'random_from_csv':
            groups = random_from_csv(self.config)
            data = data.merge(groups, on='restaurant_id', how='left')
            
        if self.config['split_method'] == 'random_from_population':
            data = random_from_population(data, self.config['group_size'])
            
        
        test_data = data[data['group'] == 'test']
        control_data = data[data['group'] == 'control']
        return test_data, control_data

    def __get(self, data):
        """
        Разделяет данные на тестовую и контрольную группы, а также на периоды до и после начала эксперимента.
        
        Параметры:
        - data (DataFrame): Данные для разделения.
        - test_group (list): Список идентификаторов ресторанов в тестовой группе.
        - control_group (list): Список идентификаторов ресторанов в контрольной группе.
        - start_date (str): Дата начала эксперимента.
        
        Возвращает:
        - data (DataFrame): Все данные с указанием статуса периода (до, во время, после).
        - test_data (DataFrame): Данные тестовой группы с указанием статуса периода.
        - control_data (DataFrame): Данные контрольной группы с указанием статуса периода.
        
        Замечание: ко всем столбцам добаляются столбцы 'group' и'status'.
        """
        test_data, control_data = self.__split_test_control(data)
        
        all_data_with_status = self.__split_before_after(data)
        test_data_with_status = self.__split_before_after(test_data)
        control_data_with_status = self.__split_before_after(control_data)
        
        return all_data_with_status, test_data_with_status, control_data_with_status
    
    def get_split(self, data):
        """
        Разделяет данные на тестовую и контрольную группы
        
        1) Считывает файл project\static\active_data\stratification_groups.csv. Путь на него указывается в common_config вручную.
            Csv-таблица представляет из себя разделение ресторанов на страты.
            Формат таблицы: 
                restraunt_id (???) | strat (int) | group (str) - Test/Control
            Пример: 
                restraunt_id,strat,group
                74021462,1,Control
                74021211,1,Test
        2) Получение массива ID ресторанов для тестовой и контрольной групп.
        3) Применение метода сплитования.
        
        Возвращает:
            DataFrame merged_data с добавленными столбцами:
                'group' и'status'
        """
        
        all_splitted_data, test_splitted_data, control_splitted_data = self.__get(data)
        
        data_dict = {
            'data': all_splitted_data,
            'data_test_before': test_splitted_data[test_splitted_data['status'] == 'before'],
            'data_control_before': control_splitted_data[control_splitted_data['status'] == 'before'],
            'data_test_after': test_splitted_data[test_splitted_data['status'] == 'after'],
            'data_control_after': control_splitted_data[control_splitted_data['status'] == 'after']
        }
        
        return data_dict