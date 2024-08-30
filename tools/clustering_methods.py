from sklearn.cluster import KMeans, DBSCAN
from sklearn import preprocessing

def kmean(data, features, norm, n_clusters, base_cluster_label, new_cluster_label):
    """
    Применяет алгоритм KMeans для кластеризации данных.

    Параметры:
    data (DataFrame): Датафрейм с данными для кластеризации.
    features (list): Список признаков для кластеризации.
    norm (bool): Флаг нормализации данных.
    n_clusters (int): Количество кластеров.
    base_cluster_label (str): Название колонки с базовыми кластерами.
    new_cluster_label (str): Название колонки для новых кластеров.

    Логика кластеризации:
    1. Если включена нормализация, применяется MinMaxScaler к указанным признакам для их масштабирования.
    2. Инициализируется алгоритм KMeans с заданным количеством кластеров.
    3. Если предыдущая метка кластера не указана (равна 'none'), применяется KMeans ко всему набору данных.
       В противном случае, кластеризация применяется отдельно к каждому подмножеству данных, соответствующему уникальным значениям в базовой метке кластера.
    4. Результаты кластеризации сохраняются в новой колонке датафрейма.

    Возвращает:
    DataFrame: Датафрейм с результатами кластеризации.
    """
    data_copy = data.copy()
    if norm:
        normalizer = preprocessing.MinMaxScaler()
        data_copy[features] = normalizer.fit_transform(data_copy[features])
        
    kmeans = KMeans(n_clusters=n_clusters)
        
    if base_cluster_label == 'none':
        cluster_labels = kmeans.fit_predict(data_copy[features])
        data[new_cluster_label] = cluster_labels
    else:
        for cluster in data[base_cluster_label].unique():
            subset = data_copy[data_copy[base_cluster_label] == cluster]
            subset_cluster_labels = kmeans.fit_predict(subset[features])
            data.loc[data[base_cluster_label] == cluster, new_cluster_label] = subset_cluster_labels
    print(data.columns)
    return data

def dbscan(data, features, norm, eps, min_samples, base_cluster_label, new_cluster_label):
    """
    Применяет алгоритм DBSCAN для кластеризации данных.

    Параметры:
    data (DataFrame): Датафрейм с данными для кластеризации.
    features (list): Список признаков для кластеризации.
    norm (bool): Флаг нормализации данных.
    eps (float): Максимальное расстояние между двумя сэмплами для их считывания в одном кластере.
    min_samples (int): Минимальное количество сэмплов в окрестности для точки, чтобы считать её ядром.
    base_cluster_label (str): Название колонки с базовыми кластерами.
    new_cluster_label (str): Название колонки для новых кластеров.

    Логика кластеризации:
    1. Если включена нормализация, применяется MinMaxScaler к указанным признакам.
    2. Инициализируется алгоритм DBSCAN с заданными параметрами eps и min_samples.
    3. Если предыдущая метка кластера не указана (равна 'none'), применяется DBSCAN ко всему набору данных.
       В противном случае, кластеризация применяется отдельно к каждому подмножеству данных, соответствующему уникальным значениям в базовой метке кластера.
    4. Результаты кластеризации сохраняются в новой колонке датафрейма.

    Возвращает:
    DataFrame: Датафрейм с результатами кластеризации.
    """
    data_copy = data.copy()
    if norm:
        normalizer = preprocessing.MinMaxScaler()
        data_copy[features] = normalizer.fit_transform(data_copy[features])

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
