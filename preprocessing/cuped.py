import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from collections import defaultdict
import tqdm

class Cuped:
    def __init__(self, config=None):
        """
        Инициализация класса CUPED.

        :param config: Конфигурация для анализа, если требуется.
        """
        self.config = config

    @staticmethod
    def calculate_theta(metrics, covariates):
        """
        Вычисляет коэффициент theta для коррекции метрики.

        :param metrics: Значения исходной метрики.
        :param covariates: Значения ковариаты.
        :return: Коэффициент theta.
        """
        covariance = np.cov(covariates, metrics)[0, 1]
        variance = covariates.var()
        theta = covariance / variance
        return theta

    def check_cuped(self, df_control, df_pilot, df_theta=None):
        """
        Проверяет гипотезу о равенстве средних с использованием CUPED.

        :param df_control: Данные контрольной группы.
        :param df_pilot: Данные экспериментальной группы.
        :param df_theta: Данные для оценки theta. Если None, используются объединенные данные контрольной и экспериментальной групп.
        :return: p-value.
        """
        if df_theta is None:
            df_theta = pd.concat([df_control, df_pilot])
        theta = self.calculate_theta(df_theta['metric'], df_theta['covariate'])
        metric_cuped_control = df_control['metric'] - theta * df_control['covariate']
        metric_cuped_pilot = df_pilot['metric'] - theta * df_pilot['covariate']
        _, pvalue = stats.ttest_ind(metric_cuped_control, metric_cuped_pilot)
        return pvalue

# Пример использования класса Cuped
# cuped_analyzer = Cuped()
# pvalue = cuped_analyzer.check_cuped(df_control, df_pilot, df_theta)
# print(f"CUPED p-value: {pvalue}")

def plot_pvalue_distribution(dict_pvalues):
    """Рисует графики распределения p-value."""
    X = np.linspace(0, 1, 1000)
    for key, pvalues in dict_pvalues.items():
        Y = [np.mean(pvalues < x) for x in X]
        plt.plot(X, Y, label=key)
    plt.plot([0, 1], [0, 1], '--k', alpha=0.8)
    plt.title('Оценка распределения p-value', size=16)
    plt.xlabel('p-value', size=12)
    plt.legend(fontsize=12)
    plt.grid()
    plt.show()

sample_size = 5000
corr = 0.7
effect = 20
dict_pvalues = defaultdict(list)

for _ in tqdm.tqdm(range(1000)):
    df_control = generate_data(sample_size, corr, mean=2000, sigma=600)
    df_pilot = generate_data(sample_size, corr, mean=2010, sigma=600)

    df_theta = pd.concat([df_control, df_pilot])
    dict_pvalues['cuped A/A'].append(check_cuped(df_control, df_pilot, df_theta))
    df_pilot['metric'] += effect
    df_theta = pd.concat([df_control, df_pilot])
    dict_pvalues['cuped A/B'].append(check_cuped(df_control, df_pilot, df_theta))
    dict_pvalues['ttest A/B'].append(check_ttest(df_control, df_pilot))

plot_pvalue_distribution(dict_pvalues)

class Cuped:
    def __init__(self, config):
        self.config = config

    def get_results(self, data_test, data_control):
        # Здесь должна быть реализация метода CUPED для анализа результатов A/B тестирования
        pass

