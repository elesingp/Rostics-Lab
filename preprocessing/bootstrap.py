import pandas as pd
from tqdm import tqdm
import numpy as np

from statistics_tools.stats import StatTests

class Bootstrap:
    def __init__(self, config):
        """
        Инициализация класса для выполнения бутстрап-тестирования.

        :param data: Данные для анализа.
        :param config: Конфигурационный словарь, содержащий настройки для тестирования.
        """
        self.config = config
        
    def do_some_viz(res, data):
        hist = plt.hist(data, bins=32, color='lightsalmon')
        ymax = hist[0][np.argmax(hist[0])]
        plt.vlines(np.mean(data), ymin=0, ymax=ymax, colors='black', 
                    label=f'Statistic mean: {np.mean(data).round(3)}')
        plt.vlines(res, ymin=0, ymax=ymax//2.5, linestyle='--', colors='black', 
                    label=f'CI: {res[0].round(3)} and {res[1].round(3)}')
        plt.xlabel('statistic value', fontsize=14)
        plt.ylabel('frequency', fontsize=14)
        plt.legend(loc=0)
        
        return None
    def quant_60(data):
        return np.quantile(data, 0.6)

    def generate_samples(self, a: pd.DataFrame, b: pd.DataFrame):
        samples = {}
        if isinstance(self.config['aggregator'], tuple):
            num_col, denom_col = self.config['aggregator']
            
            sample_sizes = {
                'b': a[num_col].count(),
                'a': b[num_col].count(),
            }

            boot1_num = a.sample(n=sample_sizes['b'], replace=True)[num_col]
            boot1_denom = a.sample(n=sample_sizes['b'], replace=True)[denom_col]

            boot2_num = b.sample(n=sample_sizes['a'], replace=True)[num_col]
            boot2_denom = b.sample(n=sample_sizes['a'], replace=True)[denom_col]

            samples['a'] = boot2_num / boot2_denom
            samples['b'] = boot1_num / boot1_denom
        else:
            aggregator = self.config['aggregator']
            sample_sizes = {
                'control': a[aggregator].count(),
                'test': b[aggregator].count(),
            }

            samples['a'] = b.sample(n=sample_sizes['test'], replace=True)[aggregator]
            samples['b'] = a.sample(n=sample_sizes['control'], replace=True)[aggregator]

        return samples

    def get_distribution(self, a: pd.DataFrame, b: pd.DataFrame):
        difference_distribution = []
        test_distribution = []
        control_distribution = []
        
        for _ in tqdm(range(self.config['bootstrap_cycles']), desc="Бутстрап", position=0, leave=True):
            samples = self.generate_samples(a, b)
            test_values = samples['a'].dropna()
            control_values = samples['b'].dropna()
                
            difference_distribution.append(test_values.mean() - control_values.mean())
            test_distribution.extend(test_values.tolist()) 
            control_distribution.extend(control_values.tolist()) 

        test_mean = np.mean(test_distribution)
        control_mean = np.mean(control_distribution)
        test_var = np.var(test_distribution, ddof=1)  # Используем ddof=1 для несмещенной оценки
        control_var = np.var(control_distribution, ddof=1)
        return {
            'difference_distribution': difference_distribution,
            'a_mean': test_mean,
            'b_mean': control_mean,
            'a_var': test_var,
            'b_var': control_var
        }
    
    def stat_results(self, a: pd.DataFrame, b: pd.DataFrame) -> dict:
        """
        Выполняет бутстрап-тестирование для сравнения контрольной и тестовой групп.

        Возвращает списки ошибок первого и второго рода, различия между группами,
        p-значения для каждого сравнения, а также ошибок I и II рода.
        
        'first_type_errors': Список, содержащий значения ошибок первого типа для каждого цикла бутстрапа.
            - Ошибка первого типа происходит, когда нулевая гипотеза отвергается, хотя на самом деле она верна.
            
        'second_type_errors': Список, содержащий значения ошибок второго типа для каждого цикла бутстрапа.
            - Ошибка второго типа происходит, когда нулевая гипотеза принимается, хотя на самом деле она неверна.
            
        'deltas_aa': Список различий между контрольными группами (A/A тестирование) для каждого цикла бутстрапа. 
            - Это помогает оценить вариативность метрики без введения изменений.
            
        'deltas_ab': Список различий между контрольной и тестовой группами (A/B тестирование) для каждого цикла бутстрапа. 
            - Это показывает, как изменение влияет на метрику.
            
        'pvalues_aa': Список p-значений для сравнения контрольных групп в каждом цикле бутстрапа. 
            - P-значение помогает определить статистическую значимость различий между группами.
            
        'pvalues_ab': Список p-значений для сравнения контрольной и тестовой групп в каждом цикле бутстрапа.
        
        't_aa_arr': Список t-статистик для сравнения контрольных групп в каждом цикле бутстрапа.
            - T-статистика используется для определения степени различия между группами.
            
        't_ab_arr': Список t-статистик для сравнения контрольной и тестовой групп в каждом цикле бутстрапа.
        """
            
        results = self.get_distribution(a, b)
        stattest = StatTests(self.config)
        stat_results = stattest.get_stats(results['difference_distribution'])

        return stat_results