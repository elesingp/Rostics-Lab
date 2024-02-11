from ..splitting import SplitData
from ..aggregation import Aggregation
from project.imports import tqdm, np, pd
from ...statistics.stats import Stats
from ...statistics.stratification import Stratification
from project.visualization import plot_histogram, plot_scatter

class SimpleCompare:
    def __init__(self, merged_data, config):
        self.merged_data = merged_data
        self.config = config
        
    def get_split(self):
        # Splitting data into test and control groups
        data = self.merged_data.copy()
        groups = pd.read_csv(self.config['groups_path'])
        test_group = groups[groups.group == 'Test'].restraunt_id.unique()
        control_group = groups[groups.group == 'Control'].restraunt_id.unique()
        return SplitData.get(data, test_group, control_group, self.config['start_date'])
    
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
            'mean_test_before': test_data[self.config['aggregator']].mean(),
            'mean_control_before': control_data[self.config['aggregator']].mean(),
            'std_test_before': test_data[self.config['aggregator']].std(),
            'std_control_before': control_data[self.config['aggregator']].std(),
            'p_value': t_test_result
        }

    def compare(self):
            AA_test_pass_list = []
            AA_results = []
            AB_results = []

            test = Stratification(self.config)
            
            # Гистограмма
            data, test_data, control_data = self.get_split() 
            agg_test_data_before, agg_control_data_before = self.get_aggregated_data_before(test_data, control_data)
            agg_test_data_after, agg_control_data_after = self.get_aggregated_data_after(test_data, control_data)
            
            agg_test = pd.concat([agg_test_data_before, agg_test_data_after]).drop_duplicates()
            agg_control = pd.concat([agg_control_data_before, agg_control_data_after]).drop_duplicates()
            #гистограмма
            histogram_path = plot_histogram(data[self.config['aggregator']], "Ген. совокупность", filename=r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\histogram.png') ## Ввести функцию
            test_histogram_path = plot_histogram(agg_test_data_before[self.config['aggregator']], "Тест-группа", filename=r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\test_histogram.png') ## Ввести функцию
            control_histogram_path = plot_histogram(agg_control_data_before[self.config['aggregator']], "Контроль-группа", filename=r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\control_histogram.png') ## Ввести функцию
            
            #график
            min = np.min([agg_control['event_date'].count(), agg_test['event_date'].count()])
            plot_path = plot_scatter(np.array(agg_test.sort_values('event_date')['event_date'])[1:min], np.array(agg_test.sort_values('event_date')[self.config['aggregator']])[1:min], np.array(agg_control.sort_values('event_date')[self.config['aggregator']])[1:min], filename=r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\plot.png') ## Ввести функцию
            
            data, test_data, control_data = self.get_split()
            agg_test_data_before, agg_control_data_before = self.get_aggregated_data_before(test_data, control_data)
            AA_p_value = test.get_p_value(agg_test_data_before, agg_control_data_before)
            AA_results.append(self.compile_results(agg_test_data_before, agg_control_data_before, AA_p_value))

            _, test_data, control_data = self.get_split()
            agg_test_data_after, agg_control_data_after = self.get_aggregated_data_after(test_data, control_data)
            AB_p_value = test.get_p_value(agg_test_data_after, agg_control_data_after)
            AB_results.append(self.compile_results(agg_test_data_after, agg_control_data_after, AB_p_value))
                
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