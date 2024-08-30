import sys
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from project.config import common_config
import pandas as pd
import tqdm
from datetime import datetime
from geopy.geocoders import Nominatim

from project.common_paths import *

def load_and_preprocess_data():
    """
    Загружает и предварительно обрабатывает данные из файлов.

    Функция сначала загружает данные о ресторанах и событиях из соответствующих файлов.
    Затем преобразует даты событий в формат '%Y-%m-%d' и фильтрует события, произошедшие до заданной даты начала.
    Удаляет ненужные столбцы из данных о ресторанах и переименовывает оставшиеся столбцы для удобства.
    Также удаляет выбранные столбцы из данных событий и переименовывает столбец 'restraunt_id' в 'Fact ID'.

    df_info - качественные данные о ресторанах.
    df_numbers - исторические данные по метрикам в ресторанах.
    Возвращает:
    df_info.
    df_numbers.
    """
    # Считываем данные о ресторанах и исторических данных по метрикам.
    df_info = pd.read_excel(df_info_path)
    #df_numbers = pd.read_csv(common_config['kiosk_path'])
    df_numbers = pd.read_csv(r'C:\ROSTICS-LAB\project\static\active_data\data_20231001_20240224.csv')
    
    # Преобразуем даты событий в формат '%Y-%m-%d' и фильтруем события, произошедшие до заданной даты начала.
    df_numbers['event_date'] = df_numbers['event_date'].apply(lambda x: datetime.strptime(str(x), "%Y%m%d").strftime("%Y-%m-%d"))
    df_numbers = df_numbers[df_numbers.event_date < common_config['start_date']]
    
    # Удаление ненужных столбцов в качественных данных о ресторанах.
    drop_columns = ['Последний тип ремоделинга', 'Код канала розничной торговли', 'Имя', 'Краткое наименование', 
                    'JDE код', 'Номер магазина', 'Группа стран/регионов', 'Адрес', 'Эл. почта', 'Телефон', 
                    'Статус', 'Статус workflow-процесса', 'WF-процессов', 'Последний год ремоделинга', 
                    'Следующий тип ремоделинга', 'Следующий год ремоделинга', 'Расширение', 
                    'Юридическое лицо франчайзи', 'Наименование юридического лица франчайзи']
    df_info = df_info.drop(drop_columns, axis=1)
    
    # Переименование столбцов в качественных данных о ресторанах.
    rename_columns = {'Внешний код Facts number': 'Fact ID', 'Цепочка компаний': 'Company Chain', 
                      'Сабдивизион': 'Subdivision', 'Рынок сбыта': 'Market Segment', 'Ценовая группа': 'Price Group', 
                      'Тип помещения': 'Room Type'}
    df_info = df_info.rename(columns=rename_columns)
    
    # Удаление выбранных столбцов из данных о ресторанах и переименование столбца'restraunt_id' в 'Fact ID'.
    #df_numbers = df_numbers.rename(columns={'restraunt_id': 'Fact ID'}).drop(['open_auth_count', 'tap_email_count', 'tap_sms_count'], axis=1)
    print(df_numbers)
    return df_info, df_numbers

def geocode_market_segments(df_info):
    """
    Геокодирует сегменты рынка, указанные в данных о ресторанах.

    Для каждого уникального сегмента рынка (обычно города или района) в данных о ресторанах
    функция использует геокодер для определения географических координат (широты и долготы).
    В случае, если название сегмента рынка не является достаточно специфичным для однозначного
    определения координат, к названию добавляется " Russia" для уточнения запроса.

    Параметры:
    df_info (DataFrame): DataFrame с данными о ресторанах, включая сегменты рынка.

    Возвращает:
    DataFrame: DataFrame с тремя столбцами: 
    'Market Segment' | 'latitude' | 'longitude',
        - название города
        - соответствующие географические координаты.
    """
    geolocator = Nominatim(user_agent="Mozilla/5.0")
    df_geo = pd.DataFrame(columns=['Market Segment', 'latitude', 'longitude'])
    city_corrections = {
        'Moscow outside MKAD': 'Moscow', 'Sholokhovo': 'Moscow', 'Cherepovetc': 'Cherepovets', 
        'Pavlovskaya Sloboda': 'Moscow', 'Vsevolojsk': 'Saint Petersburg', 'Beloozerskiy': 'Moscow', 
        'Vnukovskoye': 'Moscow', 'Mytischi': 'Moscow', 'Tolliatty': 'Tolyatti', 'Nizhniy Tagil': 'Nizhny Tagil', 
        'Ozeretskoye': 'Moscow', 'Novokuybishevsk': 'Samara', 'Voljskiy': 'Volgograd', 
        'Kamensk-Shakhtinskiy': 'Kamensk-Shakhtinsky'
    }
    
    for city in tqdm.tqdm(df_info['Market Segment'].unique()):
        corrected_city = city_corrections.get(city, city)
        if corrected_city in ['Barnaul', 'Sholokhovo', 'Orenburg', 'Moscow outside MKAD', 'Cherepovetc',                    'Kemerovo', 'Pavlovskaya Sloboda', 'Vsevolojsk', 'Beloozerskiy', 'Kazan',
                   'Vnukovskoye', 'Ufa', 'Tula', 'Engels', 'Moscow Region', 'Istra',
                   'Salavat', 'Mytischi', 'Tolliatty', 'Artyom', 'Nizhniy Tagil', 'Ozeretskoye',
                   'Suzdal', 'Marusino', 'Bratsk', 'Nazran', 'Derbent']:
            corrected_city += " Russia"

        location = geolocator.geocode(corrected_city)
        if location:
            new_row = pd.DataFrame({'Market Segment': [city], 'latitude': [location.latitude], 'longitude': [location.longitude]})
            df_geo = pd.concat([df_geo, new_row], ignore_index=True)
    return df_geo

def aggregate_data(df):
    """
    Агрегирует данные по номерам ресторанов, вычисляя среднее значение только для количественных характеристик (feature),
    исключая категориальные столбцы.

    Параметры:
    df (DataFrame): DataFrame с данными для агрегации.

    Возвращает:
    DataFrame: Агрегированные данные по каждому ресторану, включая только количественные характеристики.
    """
    # Удаление нежелательных столбцов, если они существуют
    df = df.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'], errors='ignore')
    
    # Выбор только количественных столбцов для агрегации, исключая 'restraunt_id'
    numeric_cols = df.select_dtypes(include=['number']).columns.difference(['restraunt_id'])
    
    # Агрегация данных по 'restraunt_id' с вычислением среднего значения для количественных столбцов
    aggregated_df = df.groupby('restraunt_id')[numeric_cols].mean().reset_index()
    
    return aggregated_df

def main():
    """
    Данный скрипт позволяет получить исходные данные для кластеризации ресторанов по фичам.
    Используются таблицы:
        1) df_info - описание ресторанов (какой тип ремоделинга, ценовая группа и тд).
        Формат таблицы:
            Внешний код Facts number | Рынок сбыта (Market Segment)| Ценовая группа | Статус   | Следующий год ремоделинга и тд.
                    74020442	          Ufa       Kazanskiy MoscowKFC Казанский Москва	       74020442	      
        2) df_numbers - аггрегат метрик ресторана по event_date, restraunt_id
        Формат таблицы:
            event_date | restaraunt_id | feature_i....
        3) df_geo - таблица с геоданными по рынкам сбыта (Market Segment)  \
        Формат таблицы:
            Market Segment | latitude | longitude
        
        Структура кода:
        - Выполняется препроцессинг и убираются ненужные столбцы в таблицах df_info, df_numbers
        - Выполняется получение координат(широты и долготы) для каждого сегмента рынка.
        - К таблице df_info присоединяется таблица df_geo методом "left join".
        - К таблице df_info присоединяется таблица df_numbers методом "left join".

    """
    
    # Загрузка качественных и исторических данных по всем ресторанам.
    df_info, df_numbers = load_and_preprocess_data()
    
    # Получение координат городов.
    df_geo = geocode_market_segments(df_info)
    
    # Коректировка необработанных городов вручную.
    df_info['Market Segment'] = df_info['Market Segment'].replace(city_corrections)
    # Добавление широты и долготы к качественным данным о ресторанах.
    df = df_info.merge(df_geo, on='Market Segment', how='left').drop_duplicates().rename(columns={'Fact ID': 'restraunt_id'})
    
    aggregated_df = aggregate_data(df_numbers)
    df = df.merge(aggregated_df, on='restraunt_id', how='left')
    print(df)
    # Обработка групп цен
    price_groups = ["Стандарт+50%", "Стандарт+5%", "Стандарт+30%", "Стандарт+20%", "Стандарт+15%", "Стандарт+10%", "Стандарт", "Смартбокс+20%", "Смартбокс", "Сибирь"]
    df['Price Group'] = df['Price Group'].apply(lambda x: x if x in price_groups else 0)
    df = df.drop(['Subdivision', 'Company Chain'], axis=1).astype({'Price Group': 'str'})

    # Кодирование категориальных переменных
    labelencoder = LabelEncoder()
    df['Price Group'] = labelencoder.fit_transform(df['Price Group'])
    df['Room Type'] = labelencoder.fit_transform(df['Room Type'])
    
    df.dropna().to_csv(ab_restaurant_aggregate_path)

city_corrections = {
    'Moscow outside MKAD': 'Moscow',
    'Sholokhovo': 'Moscow',
    'Cherepovetc': 'Cherepovets',
    'Pavlovskaya Sloboda': 'Moscow',
    'Vsevolojsk': 'Saint Petersburg',
    'Beloozerskiy': 'Moscow',
    'Vnukovskoye': 'Moscow',
    'Mytischi': 'Moscow',
    'Tolliatty': 'Tolyatti',
    'Nizhniy Tagil': 'Nizhny Tagil',
    'Ozeretskoye': 'Moscow',
    'Novokuybishevsk': 'Samara',
    'Voljskiy': 'Volgograd',
    'Kamensk-Shakhtinskiy': 'Kamensk-Shakhtinsky'
}

if __name__ == "__main__":
    main()