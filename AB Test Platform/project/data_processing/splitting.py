# Data Splitting
class SplitData:
    @staticmethod
    def split_before_after(data, start_date):
        data['status'] = data['event_date'].apply(lambda x: 'After' if x > start_date else 'Before' if x < start_date else 'Start')
        return data
    
    @staticmethod
    def get(data, test_group, control_group, start_date):
        data = data.copy()
        test_data = data[data['restraunt_id'].isin(test_group)].copy()
        control_data = data[data['restraunt_id'].isin(control_group)].copy()

        test_data['group'] = 'test'
        control_data['group'] = 'control'

        return SplitData.split_before_after(data, start_date), SplitData.split_before_after(test_data, start_date), SplitData.split_before_after(control_data, start_date)