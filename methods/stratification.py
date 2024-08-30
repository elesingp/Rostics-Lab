import pandas as pd
import numpy as np
from scipy import stats

from preprocessing.bootstrap import Bootstrap
from statistics_tools.stats import StatTests

class Stratification():
    def __init__(self, config, method):
        """
        Инициализирует объект класса.

        Параметры:
        - config (dict): Конфигурация метрики.
        """
        self.config = config
        self.method = method

    def calc_strat(self, a: pd.DataFrame, b: pd.DataFrame, weights: pd.Series):
        """
        Считает стратифицированное среднее.

        Параметры:
        - a (pd.DataFrame): Датафрейм с данными для страты из контрольной группы.
        - b (pd.DataFrame): Датафрейм с данными для страты из экспериментальной группы.
        - weights (pd.Series): Маппинг {название страты: вес страты в популяции}.

        Возвращает:
        - float: Стратифицированное среднее.
        """
        a_strat_means = []
        b_strat_means = []
        a_strat_vars = []
        b_strat_vars = []
        for strat in pd.concat([a, b]).strat.unique():
            a_strat = a[a.strat == strat]
            b_strat = b[b.strat == strat]  
            results = self.method.get_distribution(a_strat, b_strat)
            a_strat_means.append(results['a_mean'] * weights[strat])
            b_strat_means.append(results['b_mean'] * weights[strat])
            a_strat_vars.append(results['a_var'] * weights[strat])
            b_strat_vars.append(results['b_var'] * weights[strat])
            
        return sum(a_strat_means), sum(b_strat_means), sum(a_strat_vars), sum(b_strat_vars)
    
    def calculate_weights(self, df: pd.DataFrame) -> dict:
        """
        Рассчитывает веса для страт.

        Параметры:
        - df (pd.DataFrame): Датафрейм с данными для стратификации.

        Формула:
            Количество элементов в страте / общее количество элементов во всех стратах.
            
        Возвращает:
        - dict: Словарь с весами страт.
        """
        total_count = df.shape[0]  # Общее количество элементов в выборке
        weights = {}
        for strat in df.strat.unique():
            strat_count = df[df.strat == strat].shape[0]  # Количество элементов в текущей страте
            weights[strat] = strat_count / total_count
        return weights

    def stat_results(self, a: pd.DataFrame, b: pd.DataFrame) -> dict:
        """
        Возвращает результаты стратифицированного теста Стьюдента в виде словаря.

        Параметры:
        - a (pd.DataFrame): Данные пользователей контрольной группы.
        - b (pd.DataFrame): Данные пользователей экспериментальной группы.

        Возвращает:
        - dict: stat_results с результатами теста

        """
        df = pd.concat([a, b])
        weights = pd.Series(self.calculate_weights(df))
        a_strat_mean, b_strat_mean, a_strat_var, b_strat_var = self.calc_strat(a, b, weights)
        
        stattest = StatTests(self.config)
        a_len = a.shape[0]
        b_len = b.shape[0]
        
        params = {
            'a_mean': a_strat_mean,
            'b_mean': b_strat_mean,
            'a_var':  a_strat_var,
            'b_var':  b_strat_var,
            'a_len': a_len,
            'b_len': b_len,
        }
        stat_results = stattest.get_stats(params)
        return stat_results
    
