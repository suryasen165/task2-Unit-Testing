import pandas as pd
from io import StringIO

def process_csv(content: bytes) -> pd.DataFrame:
    """Process CSV content and return DataFrame"""
    try:
        csv_string = content.decode('utf-8')
        df = pd.read_csv(StringIO(csv_string))
        df = df.dropna()
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        raise Exception(f"Error processing CSV: {str(e)}")