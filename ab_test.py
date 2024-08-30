# Модули для работы с данными
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

class ABTest:
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
        # paraameter: metric != 0
        data = PrepareData.get(data, self.config['name'], self.config['data_collect_start_date'], self.config['data_collect_end_date'])
        if self.config['parameter'] != 'none':
            data = data.query(self.config['parameter'])
            
        return data
    
    def get_method(self):
        if self.config['method'] =='default':
            method = Default(self.config)
            
        if self.config['method'] =='bootstrap':
            method = Bootstrap(self.config)

        if self.config['method'] =='delta':
            method = Delta(self.config)
            
        if self.config['method'] =='cuped':
            method = Cuped(self.config)
            
        if self.config['method'] =='linearization':
            method = Linearization(self.config)
            
        return method
    
    def business_results(self, test_data, control_data):
        """
        Вспомогательная функция для упрощения читаемости кода.
        
        Возвращает:
        Словарь со статистическими данным.
        """
        if isinstance(self.config['aggregator'], tuple):
        
            aggregation_type_num = self.config['aggregation_type'][0]
            aggregation_type_denom = self.config['aggregation_type'][1]

            mean_test = test_data.agg({self.config['aggregator'][0]: aggregation_type_num}).iloc[0] / test_data.agg({self.config['aggregator'][1]: aggregation_type_denom}).iloc[0]
            mean_control = control_data.agg({self.config['aggregator'][0]: aggregation_type_num}).iloc[0] / control_data.agg({self.config['aggregator'][1]: aggregation_type_denom}).iloc[0]
        
            return {
                'mean_test': mean_test,
                'mean_control': mean_control,
                'sample_count': test_data.shape[0] + control_data.shape[0]
            }
        else:
            aggregation_type = self.config['aggregation_type']
            mean_test = test_data.agg({self.config['aggregator']: aggregation_type}).iloc[0] 
            mean_control = control_data.agg({self.config['aggregator']: aggregation_type}).iloc[0] 
            return {
                'mean_test': mean_test,
                'mean_control': mean_control,
                'sample_count': test_data.shape[0] + control_data.shape[0]
                #'std_test': test_data[self.config['aggregator']].std(),
                #'std_control': control_data[self.config['aggregator']].std(),
            }

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
            
        splitter = Splitter(self.config)
        filter = OutlierFilter(self.config)
        transform = Transform(self.config)
        aggregator = Aggregator(self.config)
        method = self.get_method()
        data = self.preprocess(data)
        data = filter.drop_outliers(data)
        
        data_copy = data.copy()
        
        # для стат тестов
        data = transform.get_transform(data)
        data_dict = splitter.get_split(data) 
        
        # Стратификация
        if self.config['stratification']:
            stratification = Stratification(self.config, method)
            stat_results_aa = stratification.stat_results(data_dict['data_test_before'], data_dict['data_control_before'])
            stat_results_ab = stratification.stat_results(data_dict['data_test_after'], data_dict['data_control_after'])           
        else:
            stat_results_aa = method.stat_results(data_dict['data_test_before'], data_dict['data_control_before'])
            stat_results_ab = method.stat_results(data_dict['data_test_after'], data_dict['data_control_after'])
        
        # для бизнес результатов
        data_dict_copy = splitter.get_split(data_copy) 
        
        results_aa = self.business_results(data_dict_copy['data_test_before'], data_dict_copy['data_control_before'])
        results_ab = self.business_results(data_dict_copy['data_test_after'], data_dict_copy['data_control_after'])
        
        # агрегация данных
        aggregate_dict = aggregator.get_aggregate(data_dict['data'])
        aggregate_dict_copy = aggregator.get_aggregate(data_dict_copy['data'])
        visualization_names = []

        visualization_names.append(Visualization.plot_scatter_with_ab_test_phases(self.config, aggregate_dict_copy, 'main'))
        visualization_names.append(Visualization.plot_difference_with_ab_test_phases(self.config, aggregate_dict_copy, 'main'))
        visualization_names.append(Visualization.plot_histograms_for_ab_test(self.config, data_dict, 'main', bins=15))
        print(visualization_names)
        
        results = {
            'aggregate_dict': aggregate_dict,
            'aggregate_dict_copy': aggregate_dict_copy,
            'overall_results_aa': results_aa,
            'overall_results_ab': results_ab,
            'stat_results_aa': stat_results_aa,
            'stat_results_ab': stat_results_ab,
            'visualization_names': visualization_names
        }

        return results