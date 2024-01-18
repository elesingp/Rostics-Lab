# Библиотеки для аналитики 
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Библиотеки для BigQuery
#from google.colab import auth
#from google.cloud import bigquery
#from google.colab import data_table

# Библиотеки для статистических тестов
import statsmodels.api as sm
from scipy import stats
from scipy.stats import ttest_ind, mannwhitneyu
from statsmodels.stats.proportion import proportions_ztest
from scipy.stats import ttest_ind_from_stats
from sklearn.ensemble import IsolationForest
from itertools import chain
from scipy.stats import ks_2samp

# Прочие библиотеки
import tqdm