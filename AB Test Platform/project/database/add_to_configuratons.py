from .bff import Database
from config import common_config, configurations

def add_config_in_configuration_table():
        configurations_tuples = [
        (
            config['slice_type'], 
            config['aggregator'], 
            config['aggregation_type'], 
            config['parameter'],
            config['test'],
            config['AA_alpha'],
            config['bootstrap_cycles'],
            config['distribution']
        )
        for config in configurations
        ]

        # Определите столбцы для вставки
        columns = [
            'slice_type', 'aggregator', 'aggregation_type', 'parameter',
            'test', 'AA_alpha', 'bootstrap_cycles', 'distribution'
        ]

        # Создаем экземпляр класса Database
        database = Database(common_config['dbname'], common_config['user'], common_config['host'])

        # Запускаем процедуру вставки и выборки данных
        database.run_table('configurations', configurations_tuples, columns)