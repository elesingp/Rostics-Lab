from flask import Flask, render_template, redirect, url_for, request
import pandas as pd
import json, csv
from datetime import datetime
from ast import literal_eval
import yaml
import re
from werkzeug.utils import secure_filename
import os
from ast import literal_eval
import os
from tools import Uploader
from tools.compile_results import compile_results_ab, compile_results_aa

# from database import add_config_in_configuration_table, add_abtest_in_abtest_table, Database
from designer import show_map, GetClusters
from tools.generators import generate_unique_exp_id
from common_paths import *

# Инициализация приложения
app = Flask(__name__)

# Функции для работы с данными
def load_experiments_data():
    """Загружает данные экспериментов из CSV файла и создает HTML ссылки на названии эксперимента."""
    df_experiments = pd.read_csv(experiments_path)
    df_experiments['Название эксперимента'] = df_experiments.apply(lambda row: f'<a href="/metrics/{row["exp_id"]}">{row["Название эксперимента"]}</a>', axis=1)
    return df_experiments

def initialize_dataframes_ab(exp_id):
    """Инициализирует исходные данные в DataFrame и обновляет результаты в существующих CSV файлах по ключам exp_id и metric_id."""
    global df_overall_ab, df_detailed_ab
    
    config_path = os.path.join(base_config_path, f'config_{exp_id}.yaml')  
     
    with open(config_path, 'r') as file:
        configurations = yaml.safe_load(file)
    
    #data = Uploader().upload_from_file(configurations['common_config_ab']['kiosk_path'], configurations['common_config_ab']['format'])
    data = Uploader.generate_dynamic_features_data(
        start_date='2023-10-01',
        end_date='2024-01-31',
        num_restaurants=72,
        num_sessions_per_restaurant=10
    )
    
    
    df_overall_ab_new, df_detailed_ab_new = compile_results_ab(configurations, data)

    # Проверка и обновление общих данных
    try:
        df_overall_ab_existing = pd.read_csv(overall_results_ab_path)
        if not df_overall_ab_existing.empty:
            df_overall_ab_existing = df_overall_ab_existing[df_overall_ab_existing['exp_id'] != exp_id]
            df_overall_ab = pd.concat([df_overall_ab_existing, df_overall_ab_new], ignore_index=True)
        else:
            df_overall_ab = df_overall_ab_new
    except FileNotFoundError:
        df_overall_ab = df_overall_ab_new

    # Проверка и обновление детализированных данных
    try:
        df_detailed_ab_existing = pd.read_csv(detailed_results_ab_path)
        if not df_detailed_ab_existing.empty:
            df_detailed_ab_existing = df_detailed_ab_existing[df_detailed_ab_existing['exp_id'] != exp_id]
            df_detailed_ab = pd.concat([df_detailed_ab_existing, df_detailed_ab_new], ignore_index=True)
        else:
            df_detailed_ab = df_detailed_ab_new
    except FileNotFoundError:
        df_detailed_ab = df_detailed_ab_new

    # Сохранение обновленных таблиц
    df_overall_ab.to_csv(overall_results_ab_path, index=False)
    df_detailed_ab.to_csv(detailed_results_ab_path, index=False)
    
def initialize_dataframes_aa():
    """Инициализирует исходные данные в DataFrame."""
    global df_overall_aa, df_detailed_aa
    
    #data = Uploader().upload_from_file(common_config_ab['kiosk_path'], 'csv')

    config_path = os.path.join(base_config_path, f'config_aa.yaml')  
     
    with open(config_path, 'r') as file:
        configurations = yaml.safe_load(file)
    
    data = Uploader().upload_from_file(configurations['common_config_aa']['kiosk_path'], configurations['common_config_aa']['format'])
    data = Uploader.generate_dynamic_features_data(
        start_date='2023-09-01',
        end_date='2024-01-31',
        num_restaurants=300,
        num_sessions_per_restaurant=1
    )

    df_overall_aa, df_detailed_aa = compile_results_aa(configurations, data)
    columns = ['Метрика', 'Тип', 'Канал', 'method', 'test', 'mde', 'first_type_errors', 'second_type_errors']
    df_overall_aa[columns].to_csv(overall_results_aa_path, index=False)
    df_detailed_aa.to_csv(detailed_results_aa_path, index=False)

@app.route('/')
def index():
    """Отображает главную страницу с таблицей экспериментов."""
    df_experiments = load_experiments_data().rename(columns={'exp_id': 'Номер'})
    return render_template('index1.html', table=df_experiments.to_html(escape=False, index=False))

@app.route('/create-experiment', methods=['GET', 'POST'])
def create_experiment():
    if request.method == 'POST':
        experiment_name = request.form['experiment_name']
        start_date = request.form['start_date']
        status = request.form['status']
        config_file = request.files['config_file']

        exp_id = generate_unique_exp_id()

        # Проверка, что файл присутствует
        if config_file and config_file.filename != '':
            config_path = os.path.join(base_config_path, f'config_{exp_id}.yaml') 
            config_file.save(config_path)

        with open(experiments_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([exp_id, experiment_name, start_date, status])
        return redirect(url_for('index'))
    
    return render_template('create_experiment.html')

@app.route('/edit-experiment/<int:exp_id>', methods=['GET', 'POST'])
def edit_experiment(exp_id):
    if request.method == 'POST':
        # Обработка обновленных данных формы и файла
        experiment_name = request.form['experiment_name']
        start_date = request.form['start_date']
        status = request.form['status']
        config_content = request.form['config_content']

        # Сохранение обновленных данных эксперимента
        df_experiments = pd.read_csv(experiments_path)
        df_experiments.loc[df_experiments['exp_id'] == exp_id, ['Название эксперимента', 'Дата начала', 'Статус']] = [experiment_name, start_date, status]
        df_experiments.to_csv(experiments_path, index=False, encoding='utf-8')

        # Сохранение обновленного содержимого YAML файла
        config_path = os.path.join(base_config_path, f'config_{exp_id}.yaml')  
        print(config_path)
        with open(config_path, 'w') as file:
            file.write(config_content.rstrip('\n'))
        return redirect(url_for('index'))
    else:
        df_experiments = pd.read_csv(experiments_path)
        experiment_data = df_experiments.loc[df_experiments['exp_id'] == exp_id].to_dict('records')[0]
        config_path = os.path.join(base_config_path, f'config_{exp_id}.yaml')
        with open(config_path, 'r') as file:
            config_content = file.read().rstrip('\n')

        return render_template('edit_experiment.html', exp_id=exp_id, experiment_data=experiment_data, config_content=config_content)
    
@app.route('/delete-experiment/<int:exp_id>', methods=['POST'])
def delete_experiment(exp_id):
    df_experiments = pd.read_csv(experiments_path)
    df_experiments = df_experiments[df_experiments['exp_id'] != exp_id]
    df_experiments.to_csv(experiments_path, index=False, encoding='utf-8')
    return redirect(url_for('index'))

@app.route('/delete-metric/<int:exp_id>/<int:metric_id>', methods=['POST'])
def delete_metric(exp_id, metric_id):
    global df_detailed_ab, df_overall_ab

    # Удаление метрики из детализированного DataFrame по exp_id и metric_id
    df_detailed_ab = df_detailed_ab[(df_detailed_ab['metric_id'] != metric_id) | (df_detailed_ab['exp_id'] != exp_id)]

    # Удаление метрики из общего DataFrame по exp_id и metric_id
    df_overall_ab = df_overall_ab[(df_overall_ab['metric_id'] != metric_id) | (df_overall_ab['exp_id'] != exp_id)]

    # Сохранение обновленных DataFrame в CSV
    df_detailed_ab.to_csv(detailed_results_ab_path, index=False)
    df_overall_ab.to_csv(overall_results_ab_path, index=False)

    return redirect(url_for('metrics', exp_id=exp_id))

@app.route('/metrics/<int:exp_id>')
def metrics(exp_id):
    """Отображает страницу с метриками для выбранного эксперимента."""
    global df_overall_ab, df_detailed_ab
    try:
        if not os.path.exists(overall_results_ab_path) or not os.path.exists(detailed_results_ab_path) or os.stat(overall_results_ab_path).st_size == 0 or os.stat(detailed_results_ab_path).st_size == 0:
            raise FileNotFoundError 
        
        df_overall_ab = pd.read_csv(overall_results_ab_path)
        df_detailed_ab = pd.read_csv(detailed_results_ab_path)
        
        df_overall_ab = df_overall_ab[df_overall_ab['exp_id'] == exp_id]
        df_detailed_ab = df_detailed_ab[df_detailed_ab['exp_id'] == exp_id]
        
        if df_overall_ab.empty or df_detailed_ab.empty:
            raise ValueError 
        
    except (FileNotFoundError, ValueError):
        initialize_dataframes_ab(exp_id)
        df_overall_ab = pd.read_csv(overall_results_ab_path)
        df_detailed_ab = pd.read_csv(detailed_results_ab_path)
        
        df_overall_ab = df_overall_ab[df_overall_ab['exp_id'] == exp_id]
        df_detailed_ab = df_detailed_ab[df_detailed_ab['exp_id'] == exp_id]
        
    df_metrics = df_overall_ab[df_overall_ab['exp_id'] == exp_id]
    df_metrics['Метрика_linked'] = df_metrics.apply(lambda x: f'<a href="/details/{x["metric_id"]}">{x["Метрика"]}</a>', axis=1)
    df_metrics['Удалить'] = df_metrics.apply(lambda x: f'<form action="/delete-metric/{x["exp_id"]}/{x["metric_id"]}" method="post"><button type="submit">Удалить</button></form>', axis=1)
    
    # Редактирование таблицы с метриками
    df_metrics = df_metrics[['Метрика_linked', 'Тип', 'Канал', 'До test', 'До control', 'После test', 'После control', 'Количество измерений', 'Разница', 'Разница %', 'MDE', 'p_value', 'flag', 'Удалить']].rename(columns={'Метрика_linked': 'Метрика'})
    
    config_path = os.path.join(base_config_path, f'config_{exp_id}.yaml') 
     
    with open(config_path, 'r') as file:
        configurations = yaml.safe_load(file)
        
    df_groups = pd.read_csv(configurations['common_config_ab']['groups_path'] ).sort_values(['group'], ascending=False)
    # Получение текущей даты в формате строки 'YYYY-MM-DD'

    group_counts = df_groups['group'].value_counts()

    test_info1 = pd.DataFrame({
        'Группа': ['test', 'control'],
        'Количество ресторанов': [group_counts.get('test', 0), group_counts.get('control', 0)],
    })
    test_info2 = pd.DataFrame({
        'Событие': ['Начало теста', 'Текущая дата', 'Начало сбора данных', 'Конец сбора данных'],
        'Количество ресторанов': [configurations['common_config_ab']['start_date'], datetime.now().strftime('%Y-%m-%d'), configurations['common_config_ab']['data_collect_start_date'], configurations['common_config_ab']['data_collect_end_date']],
    })
    
    return render_template('metrics.html', table=df_metrics.to_html(escape=False, index=False), exp_id=exp_id, groups=df_groups.to_html(escape=False, index=False), test_info1=test_info1.to_html(escape=False, index=False), test_info2=test_info2.to_html(escape=False, index=False))

@app.route('/refresh-metrics-ab/<int:exp_id>', methods=['POST'])
def refresh_metrics_ab(exp_id):
    """Обновляет данные эксперимента и перенаправляет на страницу метрик."""
    initialize_dataframes_ab(exp_id)
    return redirect(url_for('metrics', exp_id=exp_id))

@app.route('/refresh-metrics-aa', methods=['POST'])
def refresh_metrics_aa():
    """Обновляет данные эксперимента и перенаправляет на страницу метрик."""
    initialize_dataframes_aa()
    return redirect(url_for('aa_test'))

@app.route('/aa-test')
def aa_test():
    """Отображает результаты АА-теста."""
    try:
        if not os.path.exists(overall_results_aa_path) or os.stat(overall_results_aa_path).st_size == 0:
            raise FileNotFoundError 
        
        df_overall_aa = pd.read_csv(overall_results_aa_path)
        df_detailed_aa = pd.read_csv(detailed_results_aa_path)
        
        if df_overall_aa.empty or df_detailed_aa.empty:
            raise ValueError 
        
    except (FileNotFoundError, ValueError):
        initialize_dataframes_aa()
        df_overall_aa = pd.read_csv(overall_results_aa_path)
        df_detailed_aa = pd.read_csv(detailed_results_aa_path)
    
    visualization_names_list = df_detailed_aa['visualization_names'].values.tolist()
    print(visualization_names_list)
    return render_template('aa_test.html', table=df_overall_aa.to_html(escape=False, index=False), images=visualization_names_list)

@app.route('/details/<metric_id>')
def details(metric_id):
    """Отображает детальную информацию по выбранной метрике."""
    print(df_detailed_ab.columns)
    details_df = df_detailed_ab[df_detailed_ab['metric_id'] == int(metric_id)]

    metric_destcription = details_df[['Тест', 'Преобразование', 'Метод', 'Сплитование', 'AA pvalue']].iloc[0].to_frame().T
    metric_destcription_html = metric_destcription.to_html(classes='table table-striped', index=False)

    aggregate_path = details_df['aggregate_path'].iloc[0]

    if aggregate_path:
        aggregate_df = pd.read_csv(aggregate_path).sort_values(['group', 'Изменение, %'], ascending=False)
        aggregate_html = aggregate_df.to_html(classes='table table-striped', index=False)
    else:
        aggregate_html = "<p>Данные агрегации отсутствуют.</p>"

    visualization_names_list = literal_eval(details_df['visualization_names'].iloc[0])
    print(visualization_names_list)
    return render_template('details.html', images=visualization_names_list, metric_id=metric_id, metric_destcription_table=metric_destcription_html, aggregate_table=aggregate_html)

@app.route('/map')
def map_page():
    """
    Отображает страницу с картой, на которой показаны кластеризованные рестораны по гео и другим признакам.

    Предполагается, что функция show_map() создает карту и сохраняет ее как 'map.html' в директории 'static'. Эта страница затем отображается пользователю.

    Возвращает:
        Отрендеренный шаблон 'map_page.html', содержащий карту с результатами.
    """
    show_map()
    return render_template('map_page.html')

@app.route('/submit_restraunts', methods=['POST'])
def submit_restraunts():
    """
    Обрабатывает форму ввода идентификаторов ресторанов для A/B тестирования.

    Извлекает данные из формы, преобразует идентификаторы ресторанов в список целых чисел (если указано 'all', использует значение 'all') и передает их в функцию GetClusters для отображения кластеров ресторанов на карте.

    Возвращает:
        Перенаправление на страницу с результатами для выбранных ресторанов ('result_map').
    """
    test_restraunts = request.form['restraunts'] # 'restraunts' это имя поля ввода в форме
    
    if test_restraunts != 'all':
        test_restraunt_ids = list(map(int, test_restraunts.split(',')))
    else: 
        test_restraunt_ids = 'all'
        
    show = GetClusters(test_restraunt_ids)
    show.show_clusters_map()
    
    return redirect(url_for('result_map'))

@app.route('/result_map')
def result_map():
    """
    Отображает страницу с результатами A/B тестирования для выбранных ресторанов в виде карты.

    Использует функцию get_render класса GetClusters для генерации и отображения карты с результатами.

    Возвращает:
        Отрендеренный шаблон с картой результатов.
    """
    return GetClusters.get_render()

@app.route('/show-map-page/<int:exp_id>')
def show_map_page(exp_id):
    abtest_filter=True,
    config_path = os.path.join(config_directory_path, f'config_{exp_id}.yaml')
    with open(config_path, 'r') as file:
        configurations = yaml.safe_load(file)
    show_map(abtest_filter, configurations)
    return render_template('test_map_page.html')

# Точка входа
if __name__ == "__main__":
    app.run(debug=True)