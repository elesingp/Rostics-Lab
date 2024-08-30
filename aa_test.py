import pandas as pd
import numpy as np
import tqdm
from datetime import datetime, timedelta

from data_preparation import PrepareData 

from preprocessing.aggregate import Aggregator
from splitter.splitter import Splitter
from preprocessing.drop_outliers import OutlierFilter
import numpy as np
from preprocessing.bootstrap import Bootstrap
from methods.stratification import Stratification

from preprocessing.transform import Transform
from visualization.get_visualize_names import Visualization
from preprocessing.default import Default
from statistics_tools.simulations import Simulations

class AATest:
    """
    Класс ABTest предназначен для проведения A/B тестирования, 
    включая предобработку данных, их объединение и анализ с использованием различных статистических методов.
    """
    def __init__(self, config):
        """
        Предобработка данных из всех источников (киоск, касса и cc) и их объединение в единый набор данных.

        Этот метод последовательно вызывает функцию предобработки данных для каждого типа данных (киоск, касса, cc),
        а затем объединяет их в единый набор данных для дальнейшего анализа.
        
        Замечание: для каждого типа данных (киоск, касса, cc) предобработка данных может быть разная.
        """
        self.config = config

    def preprocess(self, data):
        """
        Предобработка данных определенного типа.
        Используется класс PrepareData в project\data_preparation\prepare_data.py для предобработки данных определенного типа.
        
        Возвращает:
            pd.DataFrame
        
        transform: default / log / sqrt / box_cox
        method: default / delta / cuped / linearization
        stratification: True / False
        """
        # Получения типа данных через метод getattr(функция озвращает значение атрибута объекта)
        return PrepareData.get(data, self.config['name'], self.config['data_collect_start_date'], self.config['data_collect_end_date'])
    
    def get_method(self):
        if self.config['method'] =='default':
            method = Default(self.config)
            
        if self.config['method'] =='bootstrap':
            method = Bootstrap(self.config)

        if self.config['method'] =='delta':
            method = Delta(self.config)
            
        if self.config['method'] =='cuped':
            method = Cuped(self.config)
            
        if self.config['method'] =='log':
            method = Linearization(self.config)
            
        return method

    def execute(self, data):
        """
        Выполнение A/B теста с использованием выбранного метода анализа.
        Метод анализа задается для каждой метрики отдельно через поле 'method' в конфигурации метрики.
        
        Получает: 
            self.merged_data (pd.DataFrame): таблица с аггрегатами:
                event_date (str): дата события в формате 'YYYY-MM-DD' |
                restraunt_id (str): идентификатор ресторана. |
                Далее фичи типа float. |
        Пример колонок: 
        ['Unnamed: 0.1', 'Unnamed: 0', 'event_date', 'restraunt_id',
       'system_identification_only_showed', 'open_auth_count',
       'tap_email_count', 'tap_sms_count', 'sessions', 'orders', 'auth_orders',
       'conversion_rate', 'auth_conversion_rate', 'revenue',
       'avg_product_count', 'strat', 'group', 'channel', 'day_of_week']
        Возвращает:
            словарь с результатами(см. классы Bootstrap и Stratification)
        """

        if "/" in self.config['aggregator']:
            self.config['aggregator'] = tuple(self.config['aggregator'].split('/'))

        if "/" in self.config['aggregation_type']:
            self.config['aggregation_type'] = tuple(self.config['aggregation_type'].split('/'))
            
        simulations = Simulations(self.config)
        splitter = Splitter(self.config)
        filter = OutlierFilter(self.config)
        transform = Transform(self.config)
        aggregator = Aggregator(self.config)
        method = self.get_method()
        data = self.preprocess(data)
        data = filter.drop_outliers(data)
        data = transform.get_transform(data)
        results_list = []
        visualization_names = []
        results = {}
        m = 0
        for mde in np.arange(self.config['MDE_start'], self.config['MDE_finish'] + self.config['MDE_step'], self.config['MDE_step']):
            pvalues_aa = []
            pvalues_ab = []
            for i in tqdm.tqdm(range(self.config['iteration_cycles'])):
                data_dict = splitter.get_split(data)
                        
                data_test_after, data_control_after = simulations.generate_effect_data(data_dict, mde)
                
                data_dict_copy = {
                    'data': data,
                    'data_test_before': data_dict['data_test_before'],
                    'data_control_before': data_dict['data_control_before'],
                    'data_test_after': data_test_after,
                    'data_control_after': data_control_after
                }

                # Стратификация
                if self.config['stratification']:
                    stratification = Stratification(self.config, method)
                    stat_results_aa = stratification.stat_results(data_dict_copy['data_test_before'], data_dict_copy['data_control_before'])
                    stat_results_ab = stratification.stat_results(data_dict_copy['data_test_after'], data_dict_copy['data_control_after'])           
                else:
                    stat_results_aa = method.stat_results(data_dict_copy['data_test_before'], data_dict_copy['data_control_before'])
                    stat_results_ab = method.stat_results(data_dict_copy['data_test_after'], data_dict_copy['data_control_after'])
                
                pvalues_aa.append(stat_results_aa['pvalue'])
                pvalues_ab.append(stat_results_ab['pvalue'])
                
            # Визуализация
            dict_pvalues = {'A/A': pvalues_aa, 'A/B': pvalues_ab}
            print(dict_pvalues)
            visualization_name = Visualization.plot_pvalue_distribution(self.config, dict_pvalues, m)
            m = m + 1
            
            first_type_error_rate = sum(p <= self.config['alpha'] for p in pvalues_aa) / len(pvalues_aa)
            second_type_error_rate = sum(p > self.config['alpha'] for p in pvalues_ab) / len(pvalues_ab)
                
            results_list.append({'mde': mde, 'first_type_errors': first_type_error_rate, 'second_type_errors': second_type_error_rate, 'visualization_name': visualization_name})

        results_df = pd.DataFrame(results_list)
        results = {
            'results_df': results_df,
        }
        return results