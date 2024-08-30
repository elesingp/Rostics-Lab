import pandas as pd
import numpy as np
from statistics_tools.stats import StatTests

class Default:
    def __init__(self, config):
        self.config = config

    def get_distribution(self, a: pd.DataFrame, b: pd.DataFrame):
        test_mean = np.mean(a[self.config['aggregator']])
        control_mean = np.mean(b[self.config['aggregator']])
        test_var = np.var(a[self.config['aggregator']], ddof=1)  # Используем ddof=1 для несмещенной оценки
        control_var = np.var(b[self.config['aggregator']], ddof=1)
        return {
            'a_mean': test_mean,
            'b_mean': control_mean,
            'a_var': test_var,
            'b_var': control_var
        }
        
    def stat_results(self, a: pd.DataFrame, b: pd.DataFrame) -> dict:
        results = self.get_distribution(a, b)
        stattest = StatTests(self.config)
        a_len = a.shape[0]
        b_len = b.shape[0]
        
        params = {
            'a_len': a_len,
            'b_len': b_len,
        }
        params.update(results)  # Correctly merge the results dictionary into params
        stat_results = stattest.get_stats(params)
            
        return stat_results