# main.py

# Импорт стандартных библиотек Python
import os

# Импорт сторонних библиотек
from flask import Flask, render_template, request, send_file, url_for, redirect
import pandas as pd
import numpy as np

from tools import Uploader # Класс для загрузки данных 
from tools import compile_results  # Модуль для сбора результатов
from config import common_config, configurations  # Конфигурационные файлы для теста
from database import add_config_in_configuration_table, add_abtest_in_abtest_table, Database  # Модули для работы с базой данных
from designer import show_map, GetClusters  # Модули для кластеризации и отображения карт
from project.common_paths import *

def run_ab_test():
    """
    Выполняет процесс A/B тестирования, загружая данные, компилируя результаты и подготавливая данные для визуализации.
    
    Эта функция выполняет следующие шаги:
    1. Загружает нужные агрегаты из указанного в config пути в pandas DataFrame. 
l      Данные аггрегаты должны находиться в папке static в разделе active_ab_tests.
    
    Формат данных: csv / excel / BigQuery / ClickHouse(не разработано) таблица "ab_{Source}_{AB Test Name}_{Test Iteration}" 
        Source - канал сбора данных(kiosk, kassa or cc)
        AB Test Name - название теста
        Test Iteration - номер итерации теста - целое число.
        пример: ab_kiosk_electronic_checks_1
    
    со столбцами 'event_date' | 'restraunt_id' | 'feature_1' | 'feature_2' | 'feature_3' | ... | 'feature_n',
    где:
        'event_date' - дата расчета метрики в формате YYYYMMDD,
        'restraunt_id' - ID ресторана(8 цифр) с типом данных ???,
        'feature_i' - значение целевой метрики с типом данных float.
        
    *Замечание: если данные какого то канал отсутствуют(например, касса), то обозначаем его пустым датафреймом:
        {Source}_data = pd.DataFrame().
        
    2. Компилирует общие результаты и статистику из загруженных данных функцией compile_results.
        Функция собирает результаты A/B тестирования и нужные пути из предоставленных данных.
        Проходится по каждой конфигурации.
        Каждая конфигурация - это метрика, заданная словарем в файле config.py
    FEATURE REQUEST: ***Добавить маппинг eng наименование на rus наименование метрик***
    
    3. Сохраняет общие результаты и статистику в файлы csv, генерирует HTML-представления и URL-адреса.
        Сохраняет в csv с помощью метода pd.DataFrame.to_csv,
        Для отображения csv таблицы получаем HTML-файл с помощью метода pd.DataFrame.to_html.
        Генерирует URL-адреса для изображений гистограмм и графиков, которые будут использоваться в веб-интерфейсе с помощью метода url_for библиотеки Flask.
        
    
    Функция завершается рендерингом шаблона 'index.html', передавая HTML-представления общих результатов,
    статистики и URL-адресов для визуализаций.
    
    Возвращает:
        Отрендеренный шаблон ('index.html') с контекстными данными, включая HTML-таблицы общих результатов и статистики,
        а также URL-адреса для изображений гистограмм и графиков.
    """
        
        
    """
    Проект A/B Тестирования Ресторанов

    Этот проект предназначен для анализа эффективности изменений в условиях работы ресторанов с использованием методологии A/B тестирования. 
    Проект включает в себя несколько ключевых компонентов, описанных ниже.

    Компоненты:
    1. Интерфейс A/B Тестирования (index.html):
        - Предоставляет пользовательский интерфейс для взаимодействия с системой A/B тестирования.
        - Включает в себя стилизацию и базовую структуру страницы для отображения результатов и управления тестами.

    2. Результаты Тестирования (overall_results.csv):
        - Содержит агрегированные результаты A/B тестирования, включая метрики до и после теста, а также статистическую значимость изменений.

    3. Извлечение Признаков (extract_features_to_table.py):
        - Обрабатывает исходные данные, извлекая необходимые признаки для анализа.
        - Агрегирует данные по ресторанам, подготавливая их для последующего анализа и кластеризации.

    4. Карта Результатов (map_results.html):
        - Предоставляет визуализацию географического распределения ресторанов и результатов тестирования.
        - Включает в себя стилизацию и структуру страницы для отображения карты с результатами.

    Структура выполнения:
    1) Вызов функции run_ab_test().
    2) Вызов функции compile_results().
    3) Выполняется метод execute класса ABTest для каждой метрики(config).
    4) Выполняется препроцесинг методом preproccess_all_data() класса ABTest.
    5) Выполнятеся метод run для одного из классов статистических методов:
            - Bootstrap
            - Stratification
    6) Данные выводятся на экран.
    """

    
    """
    Поддерживается загрузка из 'csv' и 'excel' файлов.
    """
    kiosk_data = Uploader().upload_from_file(common_config['kiosk_path'], 'csv') 
    kassa_data = pd.DataFrame() 
    cc_data = pd.DataFrame()
    print(kiosk_data)
    
    overall_results, detailed_results = compile_results(configurations, common_config, kiosk_data, kassa_data, cc_data)

    overall_results.to_csv(overall_results_file_path, index=False)
    overall_results_html = overall_results.to_html()

    detailed_results.to_csv(stats_results_file_path, index=False)
    stats_html = detailed_results.to_html()

    #add_config_in_configuration_table()

    histogram_url = url_for('static', filename=os.path.basename(histogram_file_path))
    test_histogram_url = url_for('static', filename=os.path.basename(test_histogram_file_path))
    control_histogram_url = url_for('static', filename=os.path.basename(control_histogram_file_path))
    
    plot_url = url_for('static', filename=os.path.basename(plot_file_path))

    return render_template('index.html', overall_html=overall_results_html, stats_html=stats_html, \
                          histogram_url=histogram_url, test_histogram_url=test_histogram_url, control_histogram_url=control_histogram_url, plot_url=plot_url)

app = Flask(__name__)

"""
Обработчики маршрутов для Flask приложения A/B тестирования.

Этот раздел содержит обработчики маршрутов для основных функций веб-приложения, включая:
- Отображение главной страницы и запуск A/B тестирования.
- Отображение страницы с картой результатов тестирования.
- Обработку формы для ввода идентификаторов ресторанов для тестирования.
- Отображение страницы с результатами для выбранных ресторанов.

Маршруты:
1. '/' (GET, POST): Главная страница приложения. 
При отправке формы (POST) запускает процесс A/B тестирования нажатием на кнопку "Run A/B Test" и через некоторое время отображает результаты.
2. '/map': Страница с картой, отображающей список по географическому расположению ресторанов.
3. '/submit_restraunts' (POST): Обработчик формы для ввода идентификаторов ресторанов. Позволяет выбрать конкретные рестораны для последующего сплитования.
4. '/result_map': Страница с результатами тестирования для выбранных ресторанов, отображаемая в виде карты.

Функции:
- index(): Отображает главную страницу и обрабатывает запросы на запуск A/B тестирования.
- map_page(): Отображает страницу с картой результатов тестирования.
- submit_restraunts(): Обрабатывает ввод идентификаторов ресторанов и перенаправляет на страницу с картой результатов для выбранных ресторанов.
- result_map(): Отображает страницу с картой результатов для выбранных ресторанов.

Пример использования:
Для запуска A/B тестирования пользователь отправляет форму на главной странице. После обработки данных отображаются результаты тестирования. Пользователь может также ввести идентификаторы ресторанов для анализа результатов в определенных локациях.
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Отображает главную страницу приложения и обрабатывает запросы на запуск A/B тестирования.

    При получении запроса POST (обычно отправленного из формы на главной странице) запускает процесс A/B тестирования с помощью функции run_ab_test().

    Возвращает:
        Отрендеренный шаблон 'index.html' для GET запроса или результат выполнения функции run_ab_test() для POST запроса.
    """
    if request.method == 'POST':
        return run_ab_test()
    
    return render_template('index.html')

@app.route('/create_ab_test', methods=['POST'])
def create_ab_test():
    """
    Создает новый A/B тест в базе данных на основе данных, полученных из формы.

    Функция извлекает имя теста из формы, отправленной пользователем, и добавляет информацию о тесте в таблицу базы данных с помощью функции add_abtest_in_abtest_table.

    Возвращает:
        Перенаправление на главную страницу ('index') после успешного добавления теста.
    """
    abtest_info = [
    (
        request.form['name'],
    )
    ]
    
    add_abtest_in_abtest_table(abtest_info)

    return redirect(url_for('index'))


###### FIX ####### - ошибка 404 url not found
@app.route('/download')
def download_file():
    """
    Предоставляет возможность скачать файл с общими результатами A/B тестирования.

    Функция определяет путь к файлу с результатами, который был сохранен в процессе выполнения теста, и отправляет его пользователю как вложение.

    Возвращает:
        Файл для скачивания.
    """
    path_to_file = overall_results_file_path
    return send_file(path_to_file, as_attachment=True)

@app.route('/map')
def map_page():
    """
    Отображает страницу с картой, на которой показаны кластеризованные рестораны по гео и другим признакам.

    Предполагается, что функция show_map() создает карту и сохраняет ее как 'map.html' в директории 'static'. Эта страница затем отображается пользователю.

    Возвращает:
        Отрендеренный шаблон 'map_page.html', содержащий карту с результатами.
    """
    # Предполагается, что функция show_map() создает карту и сохраняет ее как 'map.html' в 'static'
    show_map()
    return render_template('map_page.html')

# Обработчик для формы ввода идентификаторов ресторанов
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

# Страница с результатами для выбранных ресторанов
@app.route('/result_map')
def result_map():
    """
    Отображает страницу с результатами A/B тестирования для выбранных ресторанов в виде карты.

    Использует функцию get_render класса GetClusters для генерации и отображения карты с результатами.

    Возвращает:
        Отрендеренный шаблон с картой результатов.
    """
    return GetClusters.get_render()


if __name__ == "__main__":
    app.run(debug=True)
