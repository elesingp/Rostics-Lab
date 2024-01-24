import pandas as pd
import numpy as np
from datetime import datetime

def prepare_table_for_ab_test_1(data, channel, start_date, end_date):
    # Create a copy of the data to avoid SettingWithCopyWarning
    data = data.copy()

    # Your existing logic for handling different channels
    if channel in ['kassa', 'cc']:
        data = data.drop(['Franchisee Name', 'City', 'Name', 'Facility',
                          'AGC (Net)', 'Rating', 'Dish Quantity', 'Period',
                          'DoW', 'RestPick', 'Rest excl'], axis=1)
        data = data.rename(columns={'Code': 'restraunt_id',
                                    'Date': 'event_date', 'Net Sales': 'revenue',
                                    'Checs Qnt': 'order_success_count'})
    elif channel == 'kiosk':
        data['event_date'] = data['event_date'].apply(lambda x: datetime.strptime(str(x), "%Y%m%d").strftime("%Y-%m-%d"))
        data = data[['restraunt_id',  'event_date', 'revenue', 'order_success_count']]

    # Common processing
    data['channel'] = channel
    data['event_date'] = pd.to_datetime(data['event_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    data['day_of_week'] = pd.to_datetime(data['event_date'], errors='coerce').dt.day_name()

    # Filter data based on date range
    data = data[(data['event_date'] > start_date) & (data['event_date'] < end_date)]

    return data

def prepare_table_for_ab_test_2(data, channel, start_date, end_date):
    data = data.copy()

    if channel in ['kassa', 'cc']:
        return data
    
    elif channel == 'kiosk':
        data['event_date'] = data['event_date'].apply(lambda x: datetime.strptime(str(x), "%Y%m%d").strftime("%Y-%m-%d"))


        data['channel'] = channel
        data['event_date'] = pd.to_datetime(data['event_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        data['day_of_week'] = pd.to_datetime(data['event_date'], errors='coerce').dt.day_name()
        data = data[(data['event_date'] >= start_date) & (data['event_date'] <= end_date)]
        return data

class PrepareData:
    @staticmethod
    def get(data, channel, ab_test_name, start_date, end_date):
        # Specific logic for ab_test_1 and ab_test_2
        if ab_test_name in ['ab_test_1']:
            return prepare_table_for_ab_test_1(data, channel, start_date, end_date)
        if ab_test_name in ['ab_test_2']:
            return prepare_table_for_ab_test_2(data, channel, start_date, end_date)
        return data

# Data Concatenation
class Concatenation:
    def concat_data(a, b):
        return pd.concat([a, b], ignore_index=True)