from project.imports import pd, stats, np
from project.config import common_config, configurations, test_group

class Stratification():
    def __init__(self, config):
        self.config = config

    def calc_strat_mean(self, df: pd.DataFrame, weights: pd.Series) -> float:
        """Считает стратифицированное среднее.

        df - датафрейм с целевой метрикой и данными для стратификации
        weights - маппинг {название страты: вес страты в популяции}
        """
        strat_mean = df.groupby('strat')[self.config['aggregator']].mean()
        return (strat_mean * weights).sum()
    
    def calc_strat_var(self, df: pd.DataFrame, weights: pd.Series) -> float:
        """Считает стратифицированную дисперсию.
        df - датафрейм с целевой метрикой и данными для стратификации
        weights - маппинг {название страты: вес страты в популяции}
        """
        strat_var = df.groupby('strat')[self.config['aggregator']].var()
        #print(strat_var)
        return (strat_var * weights**2).sum()

    def ttest_strat(self, a: pd.DataFrame, b: pd.DataFrame, weights: pd.Series) -> float:
        """Возвращает pvalue теста Стьюдента для стратифицированного среднего.

        a, b - данные пользователей контрольной и экспериментальной групп
        weights - маппинг {название страты: вес страты в популяции}
        """
        a_strat_mean = self.calc_strat_mean(a, weights)
        b_strat_mean = self.calc_strat_mean(b, weights)
        a_strat_var = self.calc_strat_var(a, weights)
        b_strat_var = self.calc_strat_var(b, weights)
        delta = b_strat_mean - a_strat_mean
        std = (a_strat_var / len(a) + b_strat_var / len(b)) ** 0.5
        t = delta / std
        pvalue = 2 * (1 - stats.norm.cdf(np.abs(t)))
        #print(a.count(), b.count())

        #sample size
        strat_mean = self.calc_strat_mean(pd.concat([a, b]), weights)
        strat_var = self.calc_strat_var(pd.concat([a, b]), weights)

        effect = self.config['MDE']/100 * strat_mean

        t_alpha = stats.norm.ppf(1 - self.config['alpha'] / 2, loc=0, scale=1)
        t_beta = stats.norm.ppf(1 - self.config['beta'], loc=0, scale=1)
        sample_size = int((t_alpha + t_beta) ** 2 * strat_var / (effect ** 2))

        return pvalue, sample_size, strat_var, delta

    def calculate_weights(self, df):
        weights = {}
        for strat in df.strat.unique():
            add = {
                strat: (df[df.strat == strat].restraunt_id.nunique() / df.restraunt_id.nunique())
            }
            weights.update(add)

        return weights

    def get_p_value(self, a, b):
        groups = pd.read_csv(r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\test_data\groups.csv')
        a = a.merge(groups, on='restraunt_id')
        b = b.merge(groups, on='restraunt_id')
        print(a.restraunt_id.unique())
        print(b.restraunt_id.unique())
        weights = pd.Series(self.calculate_weights(pd.concat([a,b])))
        pvalue, _, _, _ = self.ttest_strat(a, b, weights)
        
        return pvalue
    