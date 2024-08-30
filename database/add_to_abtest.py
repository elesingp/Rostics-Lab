from .bff import Database
from config import common_config, configurations

def add_abtest_in_abtest_table(abtest_info):

        # Определите столбцы для вставки
        columns = [
            'name'
        ]

        # Создаем экземпляр класса Database
        database = Database(common_config['dbname'], common_config['user'], common_config['host'])

        # Запускаем процедуру вставки и выборки данных
        database.run_table('abtests', abtest_info, columns)