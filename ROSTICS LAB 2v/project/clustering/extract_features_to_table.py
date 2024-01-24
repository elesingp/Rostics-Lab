import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from project.config import common_config
from project.imports import pd, tqdm, Nominatim, geopy as gp

df_info = pd.read_excel('/workspaces/codespaces-blank/project/clustering/Рестораны (2).xlsx')
df_numbers = pd.read_csv(common_config['kiosk_path'])

df_info = df_info.drop(['Последний тип ремоделинга', 'Код канала розничной торговли',
                        'Имя', 'Краткое наименование', 'JDE код', 'Номер магазина',
                        'Группа стран/регионов', 'Адрес', 'Эл. почта', 'Телефон',
                        'Статус', 'Статус workflow-процесса', 'WF-процессов',
                        'Последний тип ремоделинга', 'Последний год ремоделинга',
                        'Следующий тип ремоделинга', 'Следующий год ремоделинга',
                        'Расширение', 'Юридическое лицо франчайзи',
                        'Наименование юридического лица франчайзи'], axis=1)

df_info = df_info.rename(columns={'Внешний код Facts number': 'Fact ID',
                        'Цепочка компаний': 'Company Chain',
                        'Сабдивизион': 'Subdivision',
                        'Рынок сбыта': 'Market Segment',
                        'Ценовая группа': 'Price Group',
                        'WF-процессов': 'Workflow Processes',
                        'Тип помещения': 'Room Type'})

df_numbers = df_numbers.rename(columns = {'restraunt_id': 'Fact ID'})
df_numbers = df_numbers.drop(['tap_auth_count', 'tap_email_count', 'tap_sms_count'], axis=1)

geolocator = Nominatim(user_agent="Mozilla/5.0")
df_geo = pd.DataFrame(columns=['Market Segment', 'latitude', 'longitude'])

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

for city in tqdm.tqdm(df_info['Market Segment'].unique()):
    if city in city_corrections:
        city = city_corrections[city]

    city_copy = city

    if city in ['Barnaul', 'Sholokhovo', 'Orenburg', 'Moscow outside MKAD', 'Cherepovetc',
                   'Kemerovo', 'Pavlovskaya Sloboda', 'Vsevolojsk', 'Beloozerskiy', 'Kazan',
                   'Kazan', 'Vnukovskoye', 'Ufa', 'Tula', 'Engels', 'Moscow Region', 'Istra',
                   'Salavat', 'Mytischi', 'Tolliatty', 'Artyom', 'Nizhniy Tagil', 'Ozeretskoye',
                   'Suzdal', 'Marusino', 'Bratsk', 'Nazran', 'Derbent']:
        city += " Russia"

    location = geolocator.geocode(city)

    if location:
        data = {'Market Segment': city_copy, 'latitude': location.latitude, 'longitude': location.longitude}
        add = pd.DataFrame(data, index=[0])
        df_geo = pd.concat([df_geo, add], ignore_index=True)

print(df_geo)

df_info['Market Segment'] = df_info['Market Segment'].replace(city_corrections)

df = df_info.merge(df_geo, on='Market Segment', how='outer').drop_duplicates()

############### ВЫБОР КОЛИЧЕСТВЕННЫХ ФИЧЕЙ ##################
aggregated_df = df_numbers.groupby('Fact ID').agg(
    action_order_success=('action_order_success', 'sum'),
    action_order_success_std=('action_order_success', 'std'),
    conversion_rate_total=('conversion_rate_total', 'mean')
)
###############################################################

df = df.merge(aggregated_df, on='Fact ID', how='inner')
price_groups = [
    "Стандарт+50%",
    "Стандарт+5%",
    "Стандарт+30%",
    "Стандарт+20%",
    "Стандарт+15%",
    "Стандарт+10%",
    "Стандарт",
    "Смартбокс+20%",
    "Смартбокс",
    "Сибирь"
]

data = df.copy()

for i in range(data['Fact ID'].count()):
  if data['Price Group'].iloc[i] not in price_groups:
    data['Price Group'].iloc[i] = 0

data = data.drop(['Subdivision', 'Company Chain'], axis=1)
data['Price Group'] = data['Price Group'].astype(str)


from sklearn.preprocessing import LabelEncoder

labelencoder = LabelEncoder()
data['Price Group'] = pd.DataFrame({"Price Group": labelencoder.fit_transform(data['Price Group'])})
data['Room Type'] = pd.DataFrame({"Room Type": labelencoder.fit_transform(data['Room Type'])})

data.to_csv('/workspaces/codespaces-blank/project/clustering/restraunt_clusters.csv')