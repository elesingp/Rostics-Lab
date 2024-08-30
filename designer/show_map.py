import folium
import yaml
import pandas as pd
from .clustering_config import colors
from flask import render_template
from tools.clustering_methods import kmean, dbscan
from common_paths import *
from sklearn.preprocessing import LabelEncoder
from tools.uploader import get_quantitative_features

def create_map(restaurants_data, latitude_column, longitude_column):
    """
    Создает карту с маркерами для каждого ресторана, используя библиотеку folium.

    Параметры:
    restaurants_data (DataFrame): Датафрейм, содержащий данные о ресторанах, включая их координаты и кластеры.
    latitude_column (str): Название столбца в датафрейме, содержащего широту.
    longitude_column (str): Название столбца в датафрейме, содержащего долготу.

    Основные шаги:
    1. Создание объекта карты с начальным местоположением, основанным на средних значениях широты и долготы.
    2. Фильтрация данных для исключения ресторанов без кластера (обозначенных как "-1.0").
    3. Итерация по отфильтрованным данным и создание маркера для каждого ресторана с соответствующим цветом кластера.
    4. Добавление маркеров на карту.

    Возвращает:
    map_object (Map): Объект карты folium с добавленными маркерами ресторанов.
    """
    map_object = folium.Map(location=[restaurants_data[latitude_column].mean(), restaurants_data[longitude_column].mean()], zoom_start=3)

    filtered_restaurants = restaurants_data[~restaurants_data['Combined_Cluster'].str.contains("-1.0")]  # Фильтрация строк с '-1'
    print(filtered_restaurants['Combined_Cluster'].nunique())
    for index, restaurant in filtered_restaurants.iterrows():  # Использование отфильтрованных данных для создания маркеров
            cluster_label = restaurant['Combined_Cluster']
            color_index = get_color_index(cluster_label)
            marker_color = colors[color_index]
            folium.Marker(
                [restaurant[latitude_column], restaurant[longitude_column]],
                icon=folium.Icon(color=marker_color),
                popup=(f"Ресторан: {restaurant.get('restraunt_id', '')}, "
                    f"Город: {restaurant['Market Segment']}, "
                    f"Помещение: {restaurant.get('Room Type', '')}, "
                    f"Ценовая группа: {restaurant.get('Price Group', '')}, "
                    f"avg_orders: {restaurant.get('avg_orders', '')}, "
                    f"sum_orders: {restaurant.get('sum_orders', '')}, "
                    f"Конверсия: {restaurant.get('conversion_rate_total', '')}, "
                    f"АБ Группа: {restaurant.get('Group', '')}, "
                    f"Cluster: {cluster_label}")
            ).add_to(map_object)
    return map_object

def show_map(abtest_filter=False, common_config_ab=None):
    """
    Создает и сохраняет карту с маркерами ресторанов, сгруппированных по кластерам.

    Эта функция сначала получает данные, прошедшие кластеризацию, затем создает карту с использованием этих данных,
    и в конце сохраняет карту в файл. Карта включает маркеры для каждого ресторана, распределенных по кластерам.
    """

    data = get_clustered_data(abtest_filter, common_config_ab)
 
    # Создание карты
    m = create_map(data, 'latitude', 'longitude')

    # сохранение карты 
    m.save(map_all_restaurants_path)
    #return render_template('show_map.html', map_file=map_file)
    
def get_color_index(value):
    """
    Возвращает индекс цвета для заданного значения.

    Индекс цвета генерируется путем применения хеш-функции к значению и взятия остатка от деления на количество доступных цветов.
    Это позволяет сопоставить каждому уникальному значению определенный цвет из предопределенного списка.

    Параметры:
    value (any): Значение, для которого требуется получить индекс цвета.

    Возвращает:
    int: Индекс цвета из списка доступных цветов.
    """
    return hash(value) % len(colors)

def create_combined_cluster_label(data, cluster_labels):
    """
    Создает комбинированную метку кластера из списка меток кластеров.

    Параметры:
    data (DataFrame): Датафрейм, содержащий данные.
    cluster_labels (list): Список строк, содержащих названия колонок с метками кластеров.

    Процесс:
    1. Создается новая колонка 'Combined_Cluster' в датафрейме.
    2. Для каждой строки в датафрейме значения из указанных колонок с метками кластеров объединяются в одну строку,
       разделенные символом подчеркивания.
    3. Полученная строка записывается в колонку 'Combined_Cluster'.

    Возвращает:
    DataFrame: Обновленный датафрейм с новой колонкой 'Combined_Cluster', содержащей комбинированные метки кластеров.
    """
    combined_label = 'Combined_Cluster'
    data[combined_label] = data[cluster_labels].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    return data

def create_map(restaurants_data, latitude_column, longitude_column):
    """
    Создает карту с маркерами для каждого ресторана, используя библиотеку folium.

    Параметры:
    restaurants_data (DataFrame): Датафрейм, содержащий данные о ресторанах, включая их координаты и кластеры.
    latitude_column (str): Название столбца в датафрейме, содержащего широту.
    longitude_column (str): Название столбца в датафрейме, содержащего долготу.

    Основные шаги:
    1. Создание объекта карты с начальным местоположением, основанным на средних значениях широты и долготы.
    2. Фильтрация данных для исключения ресторанов без кластера (обозначенных как "-1.0").
    3. Итерация по отфильтрованным данным и создание маркера для каждого ресторана с соответствующим цветом кластера.
    4. Добавление маркеров на карту.

    Возвращает:
    map_object (Map): Объект карты folium с добавленными маркерами ресторанов.
    """
    map_object = folium.Map(location=[restaurants_data[latitude_column].mean(), restaurants_data[longitude_column].mean()], zoom_start=3)

    filtered_restaurants = restaurants_data[~restaurants_data['Combined_Cluster'].str.contains("-1.0")]  # Фильтрация строк с '-1'
    print(filtered_restaurants['Combined_Cluster'].nunique())
    for index, restaurant in filtered_restaurants.iterrows():  # Использование отфильтрованных данных для создания маркеров
            cluster_label = restaurant['Combined_Cluster']
            color_index = get_color_index(cluster_label)
            marker_color = colors[color_index]
            folium.Marker(
                [restaurant[latitude_column], restaurant[longitude_column]],
                icon=folium.Icon(color=marker_color),
                popup=(f"Ресторан: {restaurant.get('restraunt_id', '')}, "
                    f"Город: {restaurant['Market Segment']}, "
                    f"Помещение: {restaurant.get('Room Type', '')}, "
                    f"Ценовая группа: {restaurant.get('Price Group', '')}, "
                    f"avg_orders: {restaurant.get('avg_orders', '')}, "
                    f"sum_orders: {restaurant.get('sum_orders', '')}, "
                    f"Конверсия: {restaurant.get('conversion_rate_total', '')}, "
                    f"АБ Группа: {restaurant.get('Group', '')}, "
                    f"Cluster: {cluster_label}")
            ).add_to(map_object)
    return map_object

def get_clustered_data(abtest_filter=False, common_config_ab=None):
    """
    Выполняет кластеризацию данных с использованием различных моделей кластеризации.

    Данная функция читает данные из указанного CSV-файла, создает копию этих данных и последовательно применяет к ним алгоритмы кластеризации в соответствии с конфигурацией, заданной в `cluster_config`. В процессе кластеризации генерируются новые метки кластеров, которые добавляются к данным. Поддерживаются алгоритмы K-Means и DBSCAN.

    Процесс кластеризации включает в себя следующие шаги:
    1. Запускаем цикл по каждому признаку(см. clustering_config.py), по которому мы хотим кластеризовать рестораны.
        Преобразовываем список признаков в строку, если в конфигурации указан список.
    2. Создание новой метки кластера на основе ключа кластера и модели.
        Формат: 
            {Название метрики}_{Модель для класеризации}_Cluster
        Пример: 
            avg_orders_Kmean_Cluster
    3. Применение модели кластеризации к данным.
    4. Создание комбинированной метки кластера из всех предыдущих меток кластеров.

    Возвращает:
        DataFrame: Данные с примененной кластеризацией и сгенерированными метками кластеров.
        Добавляются дополнительные столбцы с метками кластеров.
    """
    with open('C:\ROSTICS-LAB\project\designer\clustering_config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    restraunt_category_features_table = pd.read_csv(r'C:\ROSTICS-LAB\project\static\common_tables\restraunt_category_features_table.csv')
    restraunt_quantitative_features_table = get_quantitative_features(config)
    raw_data = restraunt_category_features_table.merge(restraunt_quantitative_features_table, on='restaurant_id', how='inner')
    print(raw_data.columns, '9999999999999999999999999999999999')
    
    print(abtest_filter)
    if abtest_filter:
        test_restraunts = pd.read_csv(common_config_ab['groups_path'])
        labelencoder = LabelEncoder()
        test_restraunts['group'] = labelencoder.fit_transform(test_restraunts['group'])
        # Use merge instead of join and specify the 'on' parameter
        raw_data = raw_data.merge(test_restraunts, on='restraunt_id', how='inner')
        cluster_config = [
        {       
            'cluster': ['group'],
            'model': 'kmean',
            'normalization': False,
            'eps / n_clusters': 2,
            'min_samples': 'none',
        },
        ]
    else: 
        cluster_config = config['cluster_config']
        
    data_for_clustering = raw_data.copy()

    # Список для хранения меток кластеров
    cluster_labels_list = []
    initial_cluster_label = 'none'
    
    # Перебор конфигураций кластеризации
    for config in cluster_config:
        # Обработка ключа кластера
        if isinstance(config['cluster'], list):
            cluster_features_key = '_'.join(config['cluster'])
        else:
            cluster_features_key = config['cluster']

        # Формирование новой метки кластера
        current_cluster_label = cluster_features_key + '_' + config['model'].capitalize() + '_Cluster'
        print(initial_cluster_label, current_cluster_label)
        cluster_labels_list.append(current_cluster_label)
        
        # Применение алгоритма кластеризации
        if config['model'] == 'kmean':
            data_for_clustering = kmean(data_for_clustering, 
                                        config['cluster'], 
                                        config['normalization'],
                                        config['eps / n_clusters'], 
                                        initial_cluster_label, 
                                        current_cluster_label)
        elif config['model'] == 'dbscan':
            data_for_clustering = dbscan(data_for_clustering, 
                                         config['cluster'], 
                                         config['normalization'],
                                         config['eps / n_clusters'], 
                                         config['min_samples'],
                                         initial_cluster_label, current_cluster_label)

        # Создание комбинированной метки кластера
        data_for_clustering = create_combined_cluster_label(data_for_clustering, cluster_labels_list)
        data_for_clustering.to_csv(restraunt_features_combined_table_path, index=False)
        initial_cluster_label = current_cluster_label
        print(cluster_labels_list, 'CLUSTER LABELS')
        print(data_for_clustering['Combined_Cluster'].nunique(), '--------------------------------------------')
        
    return data_for_clustering



class GetClusters():
    def __init__(self, test_group):
        """
        Инициализация класса для отображения кластеров ресторанов.

        Параметры:
        test_group (list): Список идентификаторов ресторанов в тестовой группе.
        """
        self.test_group = test_group

    def show_clusters_map(self):
        """
        Отображает карту с кластерами ресторанов.

        Если test_group установлено в 'all', отображаются все кластеры. 
        В противном случае отображаются только кластеры,
        включающие рестораны из тестовой группы, указанные в поисковой строке на странице карты. 
        Результаты сохраняются в файл карты.
        """
        clustered_data = pd.read_csv(restraunt_features_combined_table_path)
        result_data = pd.DataFrame()
        include_all_clusters = False
        
        # Выгрузка всех кластеров, если указано 'all'
        if self.test_group == 'all':
            include_all_clusters = True
        else:
            clustered_data['group'] = 'Control'
            clustered_data.loc[clustered_data['restaurant_id'].isin(self.test_group), 'group'] = 'Test'
            print(clustered_data['group'].unique())

        filtered_data = clustered_data[~clustered_data['Combined_Cluster'].str.contains("-1.0")]
        
        for cluster in filtered_data['Combined_Cluster'].unique():
            cluster_data = filtered_data[filtered_data['Combined_Cluster'] == cluster]
            if (include_all_clusters) or ('Test' in cluster_data['group'].unique()):
                result_data = pd.concat([result_data, cluster_data])
        
        # Сохранение карты
        map = create_map(result_data, 'latitude', 'longitude')
        map.save(map_selected_restaurants_path)
        
        # Преобразование типов данных для 'avg_orders' и 'var_orders' в числовой формат
        #import numpy as np
        #result_data[['avg_orders', 'var_orders']] = result_data[['avg_orders', 'var_orders']].astype(np.float64)
        result_data.to_csv(ab_clusters_path, index=False)

    @staticmethod
    def get_render():
        """
        Загружает результаты кластеризации и возвращает HTML для отображения на веб-странице.

        Возвращает:
        render_template: HTML-шаблон с встроенными результатами кластеризации для отображения пользователю.
        """
        result_data = pd.read_csv(ab_clusters_path)
        result_data_html = result_data.to_html()

        return render_template('map_results.html', result_html=result_data_html)