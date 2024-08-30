import pandas as pd
from splitter.splitter import Splitter

class Aggregator:
    def __init__(self, config):
        """
        Инициализирует объект класса с данными и конфигурацией.
        
        Параметры:
        - config (dict): Конфигурация исследуемой метрики.
        """
        self.config = config
        
    def aggregate(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Агрегирует данные.
        
        Параметры:
        - raw_data (DataFrame): Данные для агрегации.
        
        Возвращает:
        - aggregated_data (DataFrame): Агрегированные данные.
        """
        if isinstance(self.config['aggregator'], tuple):
            aggregation_type_num = self.config['aggregation_type'][0] 
            aggregation_type_denom = self.config['aggregation_type'][1]  
            
            group_by_columns = self.config['slice_type'].split(', ')

            if all(column in raw_data.columns for column in group_by_columns):
                aggregated_data = raw_data.groupby(group_by_columns).agg({
                    self.config['aggregator'][0]: aggregation_type_num, 
                    self.config['aggregator'][1]: aggregation_type_denom
                }).reset_index()
                
                # Создание нового столбца с результатом деления feature_1 на feature_2
                aggregated_data['ratio'] = aggregated_data[self.config['aggregator'][0]] / aggregated_data[self.config['aggregator'][1]]
                aggregator_list = list(self.config['aggregator'])
                print(aggregated_data)

                # Проверяем, есть ли уже 'ratio' в кортеже, прежде чем добавлять его
                if 'ratio' not in aggregator_list:
                    aggregator_list.append('ratio')
                    self.config['aggregator'] = tuple(aggregator_list)

            else:
                print(f"Один или несколько столбцов для группировки {group_by_columns} отсутствуют в данных.")
                return raw_data  
        else:
            group_by_columns = self.config['slice_type'].split(', ')
            aggregation_type = self.config['aggregation_type']
            if all(column in raw_data.columns for column in group_by_columns):
                aggregated_data = raw_data.groupby(group_by_columns).agg({
                    self.config['aggregator']: aggregation_type,
                }).reset_index()
                
        return aggregated_data
    
    def get_aggregate(self, raw_data):
        """
        Возвращает агрегированные данные.
        
        Параметры:
        - raw_data (DataFrame): Данные для агрегации.
        
        Возвращает:
        - aggregated_data (DataFrame): Агрегированные данные.
        """
        splitter = Splitter(self.config)
                        
        aggregate = self.aggregate(raw_data)
        aggregate_dict = splitter.get_split(aggregate) 
        return aggregate_dict
       
            