import numpy as np
from scipy import stats

class Simulations:
    def __init__(self, config):
        self.config = config

    def generate_effect_aggregate(self, aggregate_dict, mde):
        effect = mde / 100 * aggregate_dict['aggregate'][self.config['aggregator']].mean()
        print(effect)
        aggregate_test_after = aggregate_dict['aggregate_test_after'].copy()
        aggregate_control_after = aggregate_dict['aggregate_control_after'].copy()
        
        # Добавляем эффект в тестовые данные
        aggregate_test_after[self.config['aggregator']] = aggregate_test_after[self.config['aggregator']] + effect
        
        return aggregate_test_after, aggregate_control_after
    
    def generate_effect_data(self, data_dict, mde):
        if isinstance(self.config['aggregator'], tuple):
            aggregator = self.config['aggregator'][0]
        else:
            aggregator = self.config['aggregator']
            
        effect = mde / 100 * data_dict['data'][aggregator].mean()
        data_test_after = data_dict['data_test_after'].copy()
        data_control_after = data_dict['data_control_after'].copy()
        
        # Добавляем эффект в тестовые данные
        data_test_after[aggregator] = data_test_after[aggregator] + effect
        
        return data_test_after, data_control_after
        
class Gavno:
    def __init__(self, config):
        self.config = config
        self.results = {}

    def generate_simulated_values(self, group, condition_date, mu, std):
        size = self.data[(self.data['restraunt_id'].isin(group)) & condition_date][self.config['aggregator']].count()
        values = np.random.normal(mu, std, size)
        self.data.loc[(self.data['restraunt_id'].isin(group)) & condition_date, self.config['aggregator']] = values

    def simulate_values(self, mu_control, std):
        if period == 'pre':
            condition_date = self.data.event_date < self.config['common_config']['start_date']
            effect = 0
        else:
            condition_date = self.data.event_date > self.config['common_config']['start_date']
            effect = real_effect

        for group, mu in zip([test_group, control_group], [mu_control + effect, mu_control]):
            self.generate_simulated_values(group, condition_date, mu, std)

    def calculate_effects(self, control_group, test_group, real_effect):
        real_effect_percentage = round(real_effect * 100 / self.data[self.data.event_date < self.config['common_config']['start_date']][self.config['aggregator']].mean(), 2)
        self.results['real_effect_percentage'] = real_effect_percentage
        self.results['real_effect'] = real_effect
        self.calculate_sample_size()

    def calculate_sample_size(self):
        t_alpha = stats.norm.ppf(1 - self.config['alpha'] / 2)
        t_beta = stats.norm.ppf(self.config['beta'])
        effect = self.config['MDE'] / 100 * self.data[self.data.event_date < self.config['common_config']['start_date']][self.config['aggregator']].mean()
        sample_size = ((t_alpha + t_beta) ** 2 * (self.std ** 2)) / effect ** 2
        self.results['expected_effect_percentage'] = self.config['MDE']
        self.results['expected_effect'] = effect
        self.results['sample_size'] = sample_size

    def get_results(self, control_group, test_group):
        pre_control_mean = self.data[(self.data.group == "control") & (self.data.event_date < self.config['common_config']["start_date"])][self.config["aggregator"]].mean()
        pre_test_mean = self.data[(self.data.group == "test") & (self.data.event_date < self.config['common_config']["start_date"])][self.config["aggregator"]].mean()
        post_control_mean = self.data[(self.data.group == "control") & (self.data.event_date > self.config['common_config']["start_date"])][self.config["aggregator"]].mean()
        post_test_mean = self.data[(self.data.group == "test") & (self.data.event_date > self.config['common_config']["start_date"])][self.config["aggregator"]].mean()

        self.results['pre_control_mean'] = pre_control_mean
        self.results['pre_test_mean'] = pre_test_mean
        self.results['post_control_mean'] = post_control_mean
        self.results['post_test_mean'] = post_test_mean
        self.results['control_group_size'] = len(control_group)
        self.results['test_group_size'] = len(test_group)