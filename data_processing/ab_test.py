import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from project.data_preparation import PrepareData
from project.data_preparation import Concatenation  
from .methods.bootstrap import Bootstrap
from .methods.simple_compare import SimpleCompare

class ABTest:
    def __init__(self, config, kiosk_data, kassa_data, cc_data):
        self.config = config
        self.kiosk_data = kiosk_data
        self.kassa_data = kassa_data
        self.cc_data = cc_data

    def preprocess_all_data(self):
        self.kiosk_data = self.preprocess_data('kiosk')
        self.kassa_data = self.preprocess_data('kassa')
        self.cc_data = self.preprocess_data('cc')
        self.merged_data = self.merge_data() # Выводит первые несколько строк для проверки

    def preprocess_data(self, data_type):
        # Preprocessing data based on type
        data = getattr(self, f"{data_type}_data")
        return PrepareData.get(data, data_type, self.config['name'], self.config['data_collect_start_date'], self.config['data_collect_end_date'])

    def merge_data(self):
        # Merging different data sources
        return Concatenation.concat_data(self.kiosk_data, Concatenation.concat_data(self.cc_data, self.kassa_data))

    def execute(self, test_group):
        self.preprocess_all_data()
        
        if self.config['method'] == 'Simple Bootstrap':
            bootstrap_method = Bootstrap(self.merged_data, self.config, test_group, self.config['aggregator'], self.config['bootstrap_cycles'])
            results = bootstrap_method.bootstrap()
        
        if self.config['method'] == 'Simple Compare':
            simple_method = SimpleCompare(self.merged_data, self.config)
            results = simple_method.compare()

        return results
        # Обработка результатов и возврат