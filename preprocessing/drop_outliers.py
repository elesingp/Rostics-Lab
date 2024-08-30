class OutlierFilter:
    """
    Класс для фильтрации выбросов в данных.

    Этот класс предоставляет методы для удаления выбросов из набора данных на основе квантилей.
    Выбросы определяются для указанного столбца данных в соответствии с заданными границами квантилей.
    """

    def __init__(self, config):
        """
        Инициализирует экземпляр класса с конфигурацией для фильтрации.

        Параметры:
        - config (dict): Словарь конфигурации, содержащий параметры для фильтрации выбросов.
        """
        self.config = config

    def drop_outliers(self, data):
        """
        Удаляет выбросы из данных на основе квантилей.

        Параметры:
        - data (DataFrame): Данные для анализа.

        Возвращает:
        - DataFrame без выбросов.
        """
        if isinstance(self.config['aggregator'], tuple):
            num_col = self.config['aggregator'][0]
            denom_col = self.config['aggregator'][1]
            lb_num = data[num_col].quantile(self.config['lower_bound'])
            ub_num = data[num_col].quantile(self.config['upper_bound'])
            lb_denom = data[denom_col].quantile(self.config['lower_bound'])
            ub_denom = data[denom_col].quantile(self.config['upper_bound'])
            filtered_data = data[(data[num_col] >= lb_num) & (data[num_col] <= ub_num) | (data[num_col] >= lb_denom) & (data[num_col] <= ub_denom)]
            print(num_col, denom_col, lb_num, ub_num)
        else:
            lb = data[self.config['aggregator']].quantile(self.config['lower_bound'])
            ub = data[self.config['aggregator']].quantile(self.config['upper_bound'])
            filtered_data = data[(data[self.config['aggregator']] >= lb) & (data[self.config['aggregator']] <= ub)]
            
        return filtered_data