import pandas as pd
import numpy as np

from tools.generators import generate_unique_path
from common_paths import *

import matplotlib.pyplot as plt
plt.switch_backend('agg')
import seaborn as sns

class Visualization:

    @staticmethod
    def plot_histograms_for_ab_test(config, data_dict, unique_name, bins=4):
        """
        Функция для построения гистограмм для данных A/B теста.

        Эта функция принимает на вход словарь с разделенными данными для тестовой и контрольной групп до и после теста, 
        а также метрику для анализа. Для каждой группы и периода (до и после) строится гистограмма распределения указанной метрики.

        Параметры:
            data_dict (dict): Словарь с DataFrame'ами для тестовой и контрольной групп до и после теста.
            metric (str): Название метрики для анализа.
            bins (int, optional): Количество диапазонов (бинов) для гистограммы. По умолчанию равно 100.
        """
        if isinstance(config['aggregator'], tuple):
            metric = config['aggregator'][2]
        else:
            metric = config['aggregator']
        
        fig, axs = plt.subplots(2, 2, figsize=(13, 8))
        fig.suptitle(f'Гистограммы распределения метрики {metric} для A/B теста')

        axs[0, 0].hist(data_dict['data_test_before'][metric], bins=bins, color='skyblue', alpha=0.7, label='Тест до')
        axs[0, 0].set_title('Тестовая группа до')
        axs[0, 0].set_xlabel(metric)
        axs[0, 0].set_ylabel('Количество')

        axs[0, 1].hist(data_dict['data_control_before'][metric], bins=bins, color='orange', alpha=0.7, label='Контроль до')
        axs[0, 1].set_title('Контрольная группа до')
        axs[0, 1].set_xlabel(metric)
        axs[0, 1].set_ylabel('Количество')

        axs[1, 0].hist(data_dict['data_test_after'][metric], bins=bins, color='skyblue', alpha=0.7, label='Тест после')
        axs[1, 0].set_title('Тестовая группа после')
        axs[1, 0].set_xlabel(metric)
        axs[1, 0].set_ylabel('Количество')

        axs[1, 1].hist(data_dict['data_control_after'][metric], bins=bins, color='orange', alpha=0.7, label='Контроль после')
        axs[1, 1].set_title('Контрольная группа после')
        axs[1, 1].set_xlabel(metric)
        axs[1, 1].set_ylabel('Количество')

        for ax in axs.flat:
            ax.label_outer()

        path, name = generate_unique_path(config['exp_id'], config['metric_id'], 'histogram', metric, unique_name, extension='.png')
        
        plt.savefig(path)
        plt.close()

        return name

    @staticmethod
    def plot_scatter_with_ab_test_phases(config, data_dict, unique_name):
        """
        Функция для построения временного графика изменения метрики для тестовой и контрольной групп с отметкой начала A/B теста.

        Эта функция создает линейные графики для каждой из групп (тестовой и контрольной) до и после начала A/B теста, 
        а также отмечает дату начала теста на графике, чтобы визуально показать изменения в метриках до и после теста.

        Параметры:
            data_dict (dict): Словарь с DataFrame'ами для тестовой и контрольной групп до и после теста.
            metric (str): Название метрики, по которой будет строиться график.
            start_date (str): Дата начала A/B теста в формате, соответствующем формату дат в 'date'.

        Возвращает:
            str: Путь к файлу, в который был сохранен график.
        """
        if isinstance(config['aggregator'], tuple):
            metric = config['aggregator'][2]
        else:
            metric = config['aggregator']
        
        plt.figure(figsize=(10, 6))

        # Построение графиков для тестовой группы до и после начала теста
        sns.lineplot(x='date', y=metric, data=data_dict['data_test_before'], marker='o', label='Тест до')
        sns.lineplot(x='date', y=metric, data=data_dict['data_test_after'], marker='o', label='Тест после')

        # Построение графиков для контрольной группы до и после начала теста
        sns.lineplot(x='date', y=metric, data=data_dict['data_control_before'], marker='o', label='Контроль до')
        sns.lineplot(x='date', y=metric, data=data_dict['data_control_after'], marker='o', label='Контроль после')

        # Отметка даты начала A/B теста
        plt.axvline(pd.to_datetime(config['start_date']), color='red', linestyle='--', label='Начало теста')

        plt.title(f'Изменение метрики {metric} во времени')
        plt.xlabel('Дата')
        plt.ylabel('Значение метрики')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        path, name = generate_unique_path(config['exp_id'], config['metric_id'], 'plot_scatter', metric, unique_name, extension='.png')
        plt.savefig(path)
        plt.close()
        print(name)
        return name

    @staticmethod
    def plot_difference_with_ab_test_phases(config, data_dict, unique_name):
        """
        Функция для построения временного графика общей разницы метрики между тестовой и контрольной группами с отметкой начала A/B теста.

        Эта функция создает линейный график общей разницы метрик между тестовой и контрольной группами за весь период,
        а также отмечает дату начала теста на графике, чтобы визуально показать изменения в метриках.

        Параметры:
            data_dict (dict): Словарь с DataFrame'ами для тестовой и контрольной групп до и после теста.
            metric (str): Название метрики, по которой будет строиться график.
            start_date (str): Дата начала A/B теста в формате, соответствующем формату дат в 'date'.

        Возвращает:
            str: Путь к файлу, в который был сохранен график.
        """
        if isinstance(config['aggregator'], tuple):
            metric = config['aggregator'][2]
        else:
            metric = config['aggregator']
        
        plt.figure(figsize=(10, 6))

        # Объединение данных до и после в один DataFrame
        data_test = pd.concat([data_dict['data_test_before'], data_dict['data_test_after']])
        data_control = pd.concat([data_dict['data_control_before'], data_dict['data_control_after']])
        
        # Вычисление разницы метрик между тестовой и контрольной группами
        data_test = data_test.set_index('date')[metric]
        data_control = data_control.set_index('date')[metric]
        difference = data_test - data_control

        # Преобразование Series в DataFrame и сброс индекса для получения колонки с датами
        difference_df = difference.reset_index()
        difference_df.columns = ['date', metric]  # Переименование колонок для ясности

        # Построение графика разницы
        sns.lineplot(x='date', y=metric, data=difference_df, marker='o', label='Разница между группами')
        # Отметка даты начала A/B теста
        plt.axvline(pd.to_datetime(config['start_date']), color='red', linestyle='--', label='Начало теста')

        plt.title(f'Общая изменение разницы метрики {metric} между группами во времени')
        plt.xlabel('Дата')
        plt.ylabel('Разница метрики')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        path, name = generate_unique_path(config['exp_id'], config['metric_id'], 'plot_combined_difference', metric, unique_name, extension='.png')
        plt.savefig(path)
        plt.close()
        print(name)
        return name
    
    @staticmethod
    def plot_pvalue_distribution(config, dict_pvalues, unique_name):
        """Рисует графики распределения p-value."""
        X = np.linspace(0, 1, 1000)
        for name, pvalues in dict_pvalues.items():
            Y = [np.mean(pvalues < x) for x in X]
            plt.plot(X, Y, label=name)

        plt.plot([0, 1], [0, 1], '--k', alpha=0.8)
        plt.title('Оценка распределения p-value', size=16)
        plt.xlabel('p-value', size=12)
        plt.legend(fontsize=12)
        plt.grid()
        
        path, name = generate_unique_path(config['exp_id'], config['metric_id'], 'plot_pvalue_distribution', '', unique_name, extension='.png')
        plt.savefig(path)
        plt.close()
        return name

def get_visualize_paths(data, data_test, data_control, data_test_before, data_control_before, config, graphics_show):
    """
    Создает гистограммы и график рассеяния для визуализации данных.
    """
    if graphics_show:
        unique_id = config['metric_id']
        print(unique_id)
        aggregator_name = config['aggregator']

        # Генерируем уникальные пути для файлов визуализации
        unique_histogram_path = generate_unique_path(histogram_file_path, aggregator_name, unique_id)
        unique_test_histogram_path = generate_unique_path(test_histogram_file_path, aggregator_name, unique_id)
        unique_control_histogram_path = generate_unique_path(control_histogram_file_path, aggregator_name, unique_id)
        unique_plot_path = generate_unique_path(plot_file_path, aggregator_name, unique_id)

        # Визуализация гистограмм
        histogram_path = plot_histogram(data[config['aggregator']], "Ген. совокупность", filename=unique_histogram_path)
        test_histogram_path = plot_histogram(data_test_before[config['aggregator']], "Тест-группа", filename=unique_test_histogram_path)
        control_histogram_path = plot_histogram(data_control_before[config['aggregator']], "Контроль-группа", filename=unique_control_histogram_path)

        # Визуализация графика рассеяния
        min_count = np.min([data_control['date'].count(), data_test['date'].count()])
        plot_path = plot_scatter(np.array(data_test.sort_values('date')['date'])[1:min_count], 
                                np.array(data_test.sort_values('date')[config['aggregator']])[1:min_count], 
                                np.array(data_control.sort_values('date')[config['aggregator']])[1:min_count],
                                filename=unique_plot_path)

        return {
            'histogram_path': histogram_path,
            'test_histogram_path': test_histogram_path,
            'control_histogram_path': control_histogram_path,
            'plot_path': plot_path,
        }
    else:
        return {
            'histogram_path': [],
            'test_histogram_path': [],
            'control_histogram_path': [],
            'plot_path': [],
        }
        
