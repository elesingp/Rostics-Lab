# File Data Loading
import pandas as pd

class FileUploadingData:
    def __init__(self, path, format):
        self.path = path
        self.format = format

    def upload(self):
        if self.format == 'excel':
            return pd.read_excel(self.path)
        if self.format == 'csv':
            return pd.read_csv(self.path, sep=',')