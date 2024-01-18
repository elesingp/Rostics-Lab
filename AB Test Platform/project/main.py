# main.py
from flask import Flask, render_template, request, send_file, url_for
from data_loading import FileUploadingData #BigQueryUploadingData
from utilities import get_results
from config import common_config, configurations, test_group
from project.database import add_config_in_configuration_table
from project.imports import pd
import os

def run_ab_test():
    kiosk_data = FileUploadingData(common_config['kiosk_path'], 'csv').upload() #BigQueryUploadingData(common_config['project'], common_config['location'], common_config['query_id']).upload() #FileUploadingData(common_config['kiosk_path'], 'csv').upload()
    kassa_data = pd.DataFrame() #FileUploadingData(common_config['kassa_path'], 'excel').upload()
    cc_data = pd.DataFrame()#FileUploadingData(common_config['cc_path'], 'excel').upload()
    print(kiosk_data)
    
    overall_results, stats_results, \
        histogram_path, test_histogram_path, control_histogram_path  = get_results(configurations, common_config, test_group, kiosk_data, kassa_data, cc_data)

    overall_results_file = '/workspaces/codespaces-blank/project/static/ab_test_2_overall.csv'
    overall_results.to_csv(overall_results_file, index=False)
    overall_results_html = overall_results.to_html()

    stats_results_file = '/workspaces/codespaces-blank/project/static/ab_test_2_stats.csv'
    stats_results.to_csv(stats_results_file, index=False)
    stats_html = stats_results.to_html()

    add_config_in_configuration_table()

    print(histogram_path), 
    print(test_histogram_path)
    histogram_url = url_for('static', filename=os.path.basename(histogram_path))
    test_histogram_url = url_for('static', filename=os.path.basename(test_histogram_path))
    control_histogram_url = url_for('static', filename=os.path.basename(control_histogram_path))

    return render_template('index.html', overall_html=overall_results_html, stats_html=stats_html, \
                           histogram_url=histogram_url, test_histogram_url=test_histogram_url, control_histogram_url=control_histogram_url)


app = Flask(__name__)

@app.route('/download')
def download_file():
    path_to_file = 'static/ab_test_2_overall.csv'
    return send_file(path_to_file, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return run_ab_test()
    
    return render_template('index.html', overall_html='', stats_html='', histogram_url='', \
                           test_histogram_url='', control_histogram_url='')

if __name__ == "__main__":
    app.run(debug=True)
