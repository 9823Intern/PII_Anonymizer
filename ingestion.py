import pandas as pd
import PyPDF2 as pdf
class Ingestion:
    def __init__(self):
        self.data = None
    
    def load_data(self, data):
        if isinstance(data, pd.DataFrame):
            self.data = data
        elif isinstance(data, str):
            if data.endswith(".csv"):
                self.data = pd.read_csv(data)
            elif data.endswith(".xlsx"):
                self.data = pd.read_excel(data)
            elif data.endswith(".json"):
                self.data = pd.read_json(data)
            elif data.endswith(".pdf"):
                self.data = pdf.PdfReader(data)
            else:
                raise ValueError(f"Unsupported file type: {data}")
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
    def load_data_from_csv(self, data):
        self.data = pd.read_csv(data)
        
    def load_data_from_excel(self, data):
        self.data = pd.read_excel(data)
        
    def load_data_from_json(self, data):
        self.data = pd.read_json(data)
        
    def load_data_from_pdf(self, data):
        self.data = pdf.PdfReader(data)
