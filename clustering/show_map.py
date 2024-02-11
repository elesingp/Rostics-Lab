from sklearn.cluster import KMeans, DBSCAN
from sklearn import preprocessing
import folium
import pandas as pd
from .clustering_config import colors, cluster_config
from flask import Flask, render_template

def kmean(data, features, norm, n_clusters, base_cluster_label, new_cluster_label):
    data_copy = data.copy()
    if norm:
        normalizer = preprocessing.MinMaxScaler()
        data[features] = normalizer.fit_transform(data[features])
        
    kmeans = KMeans(n_clusters=n_clusters)
        
    if base_cluster_label == 'none':
        cluster_labels = kmeans.fit_predict(data_copy[features])
        data[new_cluster_label] = cluster_labels
        print('klfjwlkfwkfjbjbjb-----------------')
    else:
        print('fnijenpijijvivievev2ejvjvvkkvijevhevjeeoivieveo')
        for cluster in data[base_cluster_label].unique():
            subset = data_copy[data_copy[base_cluster_label] == cluster]
            subset_cluster_labels = kmeans.fit_predict(subset[features])
            data.loc[data[base_cluster_label] == cluster, new_cluster_label] = subset_cluster_labels
    print(data.columns)
    return data

def dbscan(data, features, norm, eps, min_samples, base_cluster_label, new_cluster_label):
    data_copy = data.copy()
    if norm:
        normalizer = preprocessing.MinMaxScaler()
        data_copy[features] = normalizer.fit_transform(data[features])

    data_copy[new_cluster_label] = -1  # Инициализация
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    
    if base_cluster_label == 'none':
        cluster_labels = dbscan.fit_predict(data_copy[features])
        data[base_cluster_label] = cluster_labels
    else:
        for cluster in data[base_cluster_label].unique():
            subset = data_copy[data_copy[base_cluster_label] == cluster]
            subset_cluster_labels = dbscan.fit_predict(subset[features])
            data.loc[data[base_cluster_label] == cluster, new_cluster_label] = subset_cluster_labels
    print(data.columns)
    return data

def create_map(data, latitude_col, longitude_col):
    m = folium.Map(location=[data[latitude_col].mean(), data[longitude_col].mean()], zoom_start=3)

    # Функция для генерации индекса цвета
    def get_color_index(value):
        return hash(value) % len(colors)

    filtered_data = data[~data['Combined_Cluster'].str.contains("-1.0")]  # Фильтрация строк с '-1'
    print(filtered_data['Combined_Cluster'].nunique())
    for index, row in filtered_data.iterrows():  # Использование отфильтрованных данных для создания маркеров
            combined_cluster = row['Combined_Cluster']
            #if '_' in combined_cluster:  # Проверяем, что это комбинированное значение
            color_index = get_color_index(combined_cluster)
            color = colors[color_index]
            folium.Marker(
                    [row[latitude_col], row[longitude_col]],
                    icon=folium.Icon(color=color),
                    popup=f"Ресторан: {row.get('Fact ID', '')}, Город: {row['Market Segment']}, Помещение: {row.get('Room Type', '')}, Ценовая группа: {row.get('Price Group', '')}, TRX: {row.get('action_order_success', '')}, \
                     TRX std: {row.get('action_order_success_std', '')}, Конверсия: {row.get('conversion_rate_total', '')}, АБ Группа: {row.get('Group', '')}, \
                     Cluster: {combined_cluster}"
            ).add_to(m)

    return m

def show_map():
    d = get_clustered_data()
    print(d, "1010013njd3je3nd3idnjnjxiejxn3jibixnj3ijn3jic3ejnxn3ejcn3")
    print(d['Combined_Cluster'])
    # Создание карты
    m = create_map(d, 'latitude', 'longitude')

    # сохранение карты
    map_file = r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\map.html'  
    m.save(map_file)
    #return render_template('show_map.html', map_file=map_file)
    
def get_color_index(value):
            return hash(value) % len(colors)

class GetClusters():
    def __init__(self, test_group):
         self.test_group = test_group

    def show_clusters_map(self):
        d = get_clustered_data()
        result_data = pd.DataFrame()

        flag = 0 
        
        # выгрузка всех класеор по ключевому слову "all"
        if self.test_group == 'all':
            flag = 1
        else:
            d['Group'] = 'Control'
            d.loc[d['Fact ID'].isin(self.test_group), 'Group'] = 'Test'
            print(d.Group.unique())

        filtered_data = d[~d['Combined_Cluster'].str.contains("-1.0")]

        for cluster in filtered_data['Combined_Cluster'].unique():
            cluster_data = filtered_data[filtered_data['Combined_Cluster'] == cluster]
            if (flag == 1) or ('Test' in cluster_data['Group'].unique()):
                result_data = pd.concat([result_data, cluster_data])
        print(result_data['Combined_Cluster'].nunique(), '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        # сохранение карты
        m = create_map(result_data, 'latitude', 'longitude')
        
        map_file = r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\map_result.html'  
        m.save(map_file)

        result_data_file = r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\clustered_results.csv'
        result_data.to_csv(result_data_file, index=False)

    @staticmethod
    def get_render():
            result_data = pd.read_csv(r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\clustered_results.csv')
            result_data_html = result_data.to_html()

            return render_template('map_results.html', result_html=result_data_html)

def create_combined_cluster_label(data, cluster_labels):
    combined_label = 'Combined_Cluster'
    data[combined_label] = data[cluster_labels].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    return data

def get_clustered_data():
    data = pd.read_csv(r'\\mosfil02.int.tgr.net\UsersFolders$\gpe9038\Desktop\ROSTICS-LAB\project\static\restraunt_clusters.csv')
    d = data.copy()

    cluster_labels = []
    base_cluster_label = 'none'
    
    for config in cluster_config:
        # Преобразование списка в строку, если 'cluster' является списком
        if isinstance(config['cluster'], list):
            cluster_key = '_'.join(config['cluster'])
        else:
            cluster_key = config['cluster']

        new_cluster_label = cluster_key + '_' + config['model'].capitalize() + '_Cluster'
        print(base_cluster_label, new_cluster_label)
        cluster_labels.append(new_cluster_label)
        if config['model'] == 'kmean':
            d = kmean(d, config['cluster'], config['normalization'],
                    config['eps / n_clusters'], base_cluster_label, new_cluster_label)
        elif config['model'] == 'dbscan':
            d = dbscan(d, config['cluster'], config['normalization'],
                    config['eps / n_clusters'], config['min_samples'],
                    base_cluster_label, new_cluster_label)

        d = create_combined_cluster_label(d, cluster_labels)
        base_cluster_label = new_cluster_label
        print(cluster_labels, 'CLUSTER LABELS')
        print(d['Combined_Cluster'].nunique(), '--------------------------------------------')
        
    return d
