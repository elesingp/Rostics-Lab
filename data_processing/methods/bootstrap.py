import random
import numpy as np
from ..splitting import SplitData
from ..aggregation import Aggregation
from project.imports import tqdm, pd
from ...statistics.stats import Stats
from project.visualization import plot_histogram, plot_scatter

class Bootstrap:
    def __init__(self, merged_data, config, test_group, aggregator, bootstrap_cycles):
        self.merged_data = merged_data
        self.config = config
        self.test_group = test_group
        self.aggregator = aggregator
        self.bootstrap_cycles = bootstrap_cycles

    def generate_control_group(self):
        # Если self.test_group не изменяется, преобразуйте его в float64 один раз вне этой функции
        test_group_float64 = np.array(self.test_group, dtype=np.float64)

        # Использование методов pandas для фильтрации
        mask = ~self.merged_data['restraunt_id'].isin(test_group_float64)
        filtered_ids = self.merged_data['restraunt_id'][mask]

        # Проверка на наличие достаточного количества уникальных ID
        if len(filtered_ids) < len(self.test_group):
            raise ValueError("Недостаточно уникальных ID для формирования контрольной группы")

        # Случайный выбор ID для контрольной группы
        control_group = np.random.choice(filtered_ids, size=len(self.test_group), replace=False)

        return control_group
        
    def get_split(self, control_group):
        # Splitting data into test and control groups
        data = self.merged_data.copy()
        return SplitData.get(data, self.test_group, control_group, self.config['start_date'])
    
    def aggregate_data(self, data, period_filter=None):
        """ Aggregates data with optional period filtering """
        if period_filter:
            data = data.query(f'status == "{period_filter}"')
        filtered_data = Aggregation.drop_outliers(data, self.config['aggregator'], self.config['lower_bound'], self.config['upper_bound'])
        aggregated_data = Aggregation.aggregate(filtered_data, self.config['slice_type'], self.config['aggregator'], self.config['aggregation_type'], self.config['parameter'])
        return aggregated_data
    
    def get_aggregated_data_before(self, test_data, control_data):
        """ Aggregate data for the period before the AB test """
        test_data_before = self.aggregate_data(test_data, 'Before')
        control_data_before = self.aggregate_data(control_data, 'Before')
        
        return test_data_before, control_data_before

    def get_aggregated_data_after(self, test_data, control_data):
        """ Aggregate data for the period after the AB test """
        test_data_after = self.aggregate_data(test_data, 'After')
        control_data_after = self.aggregate_data(control_data, 'After')

        return test_data_after, control_data_after
    
    def compile_results(self, test_data, control_data, t_test_result):
        return {
            'mean_test_before': test_data[self.aggregator].mean(),
            'mean_control_before': control_data[self.aggregator].mean(),
            'std_test_before': test_data[self.aggregator].std(),
            'std_control_before': control_data[self.aggregator].std(),
            'p_value': t_test_result
        }

    def bootstrap(self):
            AA_test_pass_list = []
            AA_results = []
            AB_results = []

            test = Stats(self.config['test'], self.config['aggregator'])
            
            # Гистограмма
            control_group = self.generate_control_group() 
            data, test_data, control_data = self.get_split(control_group) 
            agg_test_data_before, agg_control_data_before = self.get_aggregated_data_before(test_data, control_data)
            
            #гистограмма
            histogram_path = plot_histogram(data[self.aggregator], "Ген. совокупность", filename=r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\histogram.png') ## Ввести функцию
            test_histogram_path = plot_histogram(agg_test_data_before[self.aggregator], "Тест-группа", filename=r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\test_histogram.png') ## Ввести функцию
            control_histogram_path = plot_histogram(agg_control_data_before[self.aggregator], "Контроль-группа", filename=r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\control_histogram.png') ## Ввести функцию

            for _ in tqdm.tqdm(range(self.bootstrap_cycles), desc="AA Тест", position=0, leave=True):
                control_group = self.generate_control_group() 
                data, test_data, control_data = self.get_split(control_group)
                agg_test_data_before, agg_control_data_before = self.get_aggregated_data_before(test_data, control_data)
                AA_p_value = test.get_p_value(agg_test_data_before, agg_control_data_before)
                if self.config['AA_alpha'] < AA_p_value < 2: 
                    agg_test_before = agg_test_data_before
                    agg_control_before = agg_control_data_before
                    AA_test_pass_list.append(control_group)
                    AA_results.append(self.compile_results(agg_test_data_before, agg_control_data_before, AA_p_value))

            for control_group in tqdm.tqdm(AA_test_pass_list, desc="AБ Тест", position=0, leave=True):
                _, test_data, control_data = self.get_split(control_group)
                agg_test_data_after, agg_control_data_after = self.get_aggregated_data_after(test_data, control_data)
                print(control_group)
                agg_test_after = agg_test_data_after
                agg_control_after = agg_control_data_after
                
                AB_p_value = test.get_p_value(agg_test_data_after, agg_control_data_after)
                AB_results.append(self.compile_results(agg_test_data_after, agg_control_data_after, AB_p_value))

            #график
            #график
            agg_test = pd.concat([agg_test_before, agg_test_after]).drop_duplicates()
            agg_control = pd.concat([agg_control_before, agg_control_after]).drop_duplicates()
            min = np.min([agg_control['event_date'].count(), agg_test['event_date'].count()])
            plot_path = plot_scatter(np.array(agg_test['event_date'])[1:min], np.array(agg_test[self.config['aggregator']])[1:min], np.array(agg_control[self.config['aggregator']])[1:min], filename=r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\plot.png') ## Ввести функцию
            
            return {
                'merged_data': self.merged_data,
                'AA_test_pass_list': AA_test_pass_list,
                'AA_average_p_value': np.mean([result['p_value'] for result in AA_results]),
                'AB_average_p_value': np.mean([result['p_value'] for result in AB_results]),
                'AA_results': AA_results,
                'AB_results': AB_results,
                'data_histogram_path': histogram_path,
                'test_data_histogram_path': test_histogram_path,
                'control_data_histogram_path': control_histogram_path,
                'plot_path': plot_path,
            }