from multiprocessing import AuthenticationError
from google.oauth2 import service_account
from google.cloud import bigquery
import os    

# Путь к файлу с ключами сервисного аккаунта
key_path = "/workspaces/codespaces-blank/kfc-kiosk-3-57d0888cd7fd.json"

# Аутентификация и создание клиента для BigQuery
credentials = service_account.Credentials.from_service_account_file(key_path)
client = bigquery.Client(credentials=credentials)

print(credentials)
class BigQueryUploadingData:
    def __init__(self, project, location, query_id):
        self.project = project
        self.location = location
        self.query_id = query_id
        self.client = bigquery.Client(project=project, location=location)

    def get_job(self):
        job = self.client.get_job(self.query_id)
        print(credentials)
        return job.to_dataframe()

    def upload(self):
        return self.get_job()
