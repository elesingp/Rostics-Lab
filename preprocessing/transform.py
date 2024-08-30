import numpy as np
import pandas as pd
from scipy.stats import boxcox
from sklearn.preprocessing import PowerTransformer

class Transform:
    def __init__(self, config):
        self.config = config

    def get_transform(self, df):
        method = self.config.get('transform', 'default')
        column = self.config['aggregator']

        if method == 'log':
            df[column] = np.log(df[column] + 1)  # Adding 1 to avoid log(0)
        elif method == 'sqrt':
            df[column] = np.sqrt(df[column])
        elif method == 'box_cox':
            # Box-Cox transformation requires all data to be positive
            positive_data = df[column] + 1 - df[column].min()  # Shifting data to be strictly positive
            df[column], _ = boxcox(positive_data)
        # 'default' or any other method requires no action, so it's passed
        return df