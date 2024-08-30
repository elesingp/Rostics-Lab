import yaml

with open('C:\ROSTICS-LAB\project\configs\config_9.yaml', 'r') as file:
    configurations = yaml.safe_load(file)

print(configurations['configurations_ab'])

aggregate_dict = {
    'aggregate': aggregate,
    'aggregate_test_before': aggregate_test[aggregate_test['status'] == 'before'],
    'aggregate_control_before': aggregate_control[aggregate_control['status'] == 'before'],
    'aggregate_test_after': aggregate_test[aggregate_test['status'] == 'after'],
    'aggregate_control_after': aggregate_control[aggregate_control['status'] == 'after']
}

# Преобразование словаря results в отдельные столбцы для каждого элемента в словаре
expanded_results = results_df['results'].apply(pd.Series)

# Добавление столбца mde к расширенному датафрейму
expanded_results['mde'] = results_df['mde']
expanded_results = expanded_results[['mde', 'results_aa', 'results_ab']]
expanded_results_aa = expanded_results['results_aa'].apply(pd.Series)
expanded_results_ab = expanded_results['results_ab'].apply(pd.Series)
expanded_results_aa['mde'] = results_df['mde']
expanded_results_ab['mde'] = results_df['mde']

# Объединение DataFrame expanded_results_aa и expanded_results_ab по индексу
expanded_results_merged = expanded_results_aa.join(
    expanded_results_ab, 
    lsuffix='_aa', 
    rsuffix='_ab'
).reset_index(drop=True)

averaged_results_by_mde = expanded_results_merged.groupby('mde_aa').mean().reset_index()
final_results = averaged_results_by_mde[['mde_aa','first_type_errors_aa','second_type_errors_ab']]
print(final_results)
print(final_results.dtypes)