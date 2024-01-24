import matplotlib.pyplot as plt
import os

def plot_histogram(df, type, bins=100, filename='/workspaces/codespaces-blank/project/static/histogram.png'):
    """
    Функция принимает DataFrame с одним столбцом и строит гистограмму.
    
    Параметры:
    df (pandas.DataFrame): DataFrame с одним столбцом.
    bins (int): Количество диапазонов (бинов) для гистограммы.
    """
    # Строим гистограмму
    plt.hist(df, bins=bins)
    plt.xlabel('Значения')
    plt.ylabel('Количество')
    plt.title(type)
    plt.show()

    # Сохранение изображения в статическую директорию
    path = os.path.join('static', filename)
    plt.savefig(path)
    plt.close()

    return path






