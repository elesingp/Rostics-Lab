configurations = [
    {
        'slice_type': 'event_date, restraunt_id',
        'aggregator': 'revenue',
        'aggregation_type': 'sum',
        'parameter': 'none',
        'test': 'ttest_2sample', #  74021433
        'AA_alpha': 0,
        'bootstrap_cycles': 10,
        'method': 'Simple Bootstrap' 
    },
]

# Common configuration
common_config = {
    'dbname': 'db', 
    'user': 'codespace', 
    'host': 'localhost',
    'project': 'kfc-kiosk-3',
    'location': 'US',
    'query_id': 'bquxjob_159f1b6a_18cedf71333',
    'kiosk_path': '/workspaces/codespaces-blank/bquxjob_567f0b61_18cf4ee3d07.csv',
    'cc_path': '/workspaces/codespaces-blank/cc.xlsx',
    'kassa_path': '/workspaces/codespaces-blank/kassa.xlsx',
    'name': 'ab_test_2',
    'start_date': '2023-12-16',
    'data_collect_start_date': '2023-11-06',
    'data_collect_end_date': '2024-01-08',
    'lower_bound': 0,
    'upper_bound': 1
}

# Test group IDs
test_group = [74020587, 74020449, 74021433, 74021788, 74021978, 74020828, 74021003, 74021914, 74021880, 74021975, 
              74321670, 74215106, 74021639, 74021302, 74021329, 74020871, 74020660, 74021678, 74021928, 74020551]