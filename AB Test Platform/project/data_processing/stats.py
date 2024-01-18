import statsmodels.api as sm
import pandas as pd
from scipy import stats
from scipy.stats import ttest_ind, mannwhitneyu
from statsmodels.stats.proportion import proportions_ztest
from scipy.stats import ttest_ind_from_stats, ks_2samp
from sklearn.ensemble import IsolationForest
from project.imports import np

# Statistical Analysis
class Stats:
    def __init__(self, test, aggregator):
        self.test = test
        self.aggregator = aggregator

    @staticmethod
    def get_stats(data):
        return data.mean(), data.std(ddof=1), data.count()

    def mannwhitneyu_test(a, b, aggregator):
        _, p_value = mannwhitneyu(a[aggregator], b[aggregator])
        return p_value

    def ks_2samp_test(self, a, b, aggregator):
        _, p_value = stats.ks_2samp(np.array(a[aggregator]), np.array(b[aggregator]), alternative='two_sided', method='exact')
        return p_value

    def two_sample_ttest(self, a, b, aggregator):
        # Check if 'a' and 'b' are DataFrames and 'aggregator' is a valid column
        if not isinstance(a, pd.DataFrame) or not isinstance(b, pd.DataFrame) or \
           aggregator not in a.columns or aggregator not in b.columns:
            raise ValueError("Input data must be DataFrames and the aggregator must be a valid column name.")
        abar, astd, na = Stats.get_stats(a[aggregator])
        bbar, bstd, nb = Stats.get_stats(b[aggregator])
        _, p_value = ttest_ind_from_stats(abar, astd, na,
                                    bbar, bstd, nb,
                                    equal_var=True)
        return p_value
    
    def get_p_value(self, a, b):
        if self.test == 'kolmogorov_2sample':
            return self.ks_2samp_test(a, b, self.aggregator)
        if self.test == 'ttest_2sample':
            return self.two_sample_ttest(a, b, self.aggregator)