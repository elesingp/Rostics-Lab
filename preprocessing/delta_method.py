import pandas as pd

class Delta:
    def __init__(self, config):
        self.config = config

    def get_results(self, data_test, data_control):
        # Здесь должна быть реализация метода Delta для анализа результатов A/B тестирования
        pass
    
    def stat_results(self, a: pd.DataFrame, b: pd.DataFrame) -> dict:
        pass