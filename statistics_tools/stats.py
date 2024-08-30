import statsmodels.api as sm
import pandas as pd
from scipy import stats
from scipy.stats import ttest_ind, mannwhitneyu
from statsmodels.stats.proportion import proportions_ztest
from scipy.stats import ttest_ind_from_stats, ks_2samp
from sklearn.ensemble import IsolationForest
from tools.imports import np

# Statistical Analysis
class StatTests:
    def __init__(self, config):
        """
        Инициализирует объект класса Stats для проведения статистического анализа.

        :param config: Словарь конфигурации, содержащий параметры для анализа.
        """
        self.config = config

    def get_parameters(self, data):
        """
        Возвращает основные статистические характеристики данных в виде словаря.

        :param data: Данные для анализа.
        :return: Словарь с основными статистическими характеристиками: среднее, стандартное отклонение и количество элементов.
        """
        return {'mean': data.mean(), 'std_dev': data.std(ddof=1), 'count': data.count()}
    
    def mannwhitneyu_test(self, a, b):
        """
        Выполняет тест Манна-Уитни для двух независимых выборок и возвращает результат в виде словаря.

        :param a: Первая выборка данных.
        :param b: Вторая выборка данных.
        :return: Словарь с p-значением теста Манна-Уитни.
        """
        _, p_value = mannwhitneyu(a[self.config['aggregator']], b[self.config['aggregator']])
        return {'pvalue': p_value}
    
    def ks_2samp_test(self, a, b):
        """
        Выполняет двухвыборочный тест Колмогорова-Смирнова для проверки гипотезы о равенстве распределений двух выборок и возвращает результат в виде словаря.

        :param a: Первая выборка данных.
        :param b: Вторая выборка данных.
        :return: Словарь с p-значением двухвыборочного теста Колмогорова-Смирнова.
        """
        _, p_value = ks_2samp(np.array(a[self.config['aggregator']]), 
                              np.array(b[self.config['aggregator']]), 
                              alternative='two_sided', 
                              method='exact')
        return {'pvalue': p_value}

    def mann_whitney_u_test(self, a, b):
        """
        Выполняет тест Манна-Уитни для двух независимых выборок и возвращает результат в виде словаря.

        :param a: Первая выборка данных.
        :param b: Вторая выборка данных.
        :return: Словарь с p-значением теста Манна-Уитни.
        """
        # Извлекаем данные по ключу из конфигурации
        data_a = a[self.config['aggregator']]
        data_b = b[self.config['aggregator']]

        # Выполнение теста Манна-Уитни
        u_statistic, p_value = mannwhitneyu(data_a, data_b, alternative='two-sided')

        # Возвращаем результат в виде словаря
        return {'u_statistic': u_statistic, 'pvalue': p_value}

    def two_sample_ttest(self, a, b):
        """
        Выполняет двухвыборочный t-тест для проверки гипотезы о равенстве средних двух независимых выборок и возвращает результат в виде словаря.

        :param a: Первая выборка данных.
        :param b: Вторая выборка данных.
        :return: Словарь с p-значением двухвыборочного t-теста.
        """
        stats_a = self.get_parameters(a[self.config['aggregator']])
        stats_b = self.get_parameters(b[self.config['aggregator']])
        _, p_value = ttest_ind_from_stats(stats_a['mean'], stats_a['std_dev'], stats_a['count'],
                                          stats_b['mean'], stats_b['std_dev'], stats_b['count'],
                                          equal_var=True)
        return {'pvalue': p_value}
    
    def ci_test(self, stat_distrib):
        # confidence interval counting
        left_q = (self.config['alpha']) / 2
        right_q = 1 - left_q
        ci = np.quantile(stat_distrib, [left_q, right_q])
        
        # p_value
        quant = stats.norm.cdf(x=0, loc=np.mean(stat_distrib), scale=np.std(stat_distrib, ddof=1))
        p_value = quant * 2 if 0 < np.mean(stat_distrib) else (1 - quant) * 2
        return {'pvalue': p_value}
    
    def ttest_1samp(self, distribution):
        _, pvalue = stats.ttest_1samp(distribution, 0)
        return {'pvalue': pvalue}
    def calculator_ttest(self, params):
        delta = params['a_mean'] - params['b_mean']
        std = (params['a_var'] / params['a_len'] + params['b_var'] / params['b_len']) ** 0.5
        t = delta / std
        pvalue = 2 * (1 - stats.norm.cdf(np.abs(t)))
        return {'pvalue': pvalue}

    
    def get_stats(self, a, b=None):
        """
        Определяет и возвращает p-значение выбранного статистического теста, указанного в конфигурации.

        :param a: Первая выборка данных.
        :param b: Вторая выборка данных.
        :return: p-значение выбранного статистического теста.
        """

        if self.config['test'] == 'kolmogorov':
            return self.ks_2samp_test(a, b)
        if (self.config['stratification'] == False) & (self.config['test'] == 'ttest') & (self.config['method'] == 'bootstrap'):
            return self.ttest_1samp(a)
        if ((self.config['test'] == 'ttest') | (self.config['test'] == 'mwtest')) & (self.config['method'] == 'default'): 
            return self.calculator_ttest(a)
        if (self.config['stratification'] == False) & (self.config['test'] == 'mwtest') & (self.config['method'] == 'default'): 
            return self.mann_whitney_u_test(a, b)
        if (self.config['stratification'] == False) & (self.config['test'] == 'ci') & (self.config['method'] == 'bootstrap'):    
            return self.ci_test(a)
        if (self.config['stratification'] == True) & (self.config['test'] == 'ttest') & (self.config['method'] == 'bootstrap'):
            return self.calculator_ttest(a)