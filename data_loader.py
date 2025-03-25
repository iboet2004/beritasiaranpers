import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

def load_dataset(dataset_name):
    """
    Load dataset from Google Sheets
    
    Args:
        dataset_name (str): Name of the dataset to load
    
    Returns:
        pd.DataFrame: Loaded dataset
    """
    try:
        # Load credentials from Streamlit secrets
        credentials = {
            "type": st.secrets["gcp"]["type"],
            "project_id": st.secrets["gcp"]["project_id"],
            "private_key_id": st.secrets["gcp"]["private_key_id"],
            "private_key": st.secrets["gcp"]["private_key"],
            "client_email": st.secrets["gcp"]["client_email"],
            "client_id": st.secrets["gcp"]["client_id"],
            "auth_uri": st.secrets["gcp"]["auth_uri"],
            "token_uri": st.secrets["gcp"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gcp"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gcp"]["client_x509_cert_url"]
        }
        
        # Setup the credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
        client = gspread.authorize(creds)
        
        # Map dataset names to specific spreadsheet and worksheet
        dataset_map = {
            "DATASET SP": {
                "spreadsheet_id": st.secrets["spreadsheets"]["sp_spreadsheet_id"],
                "worksheet_name": "DATASET SP"  # Adjust as needed
            },
            "DATASET BERITA": {
                "spreadsheet_id": st.secrets["spreadsheets"]["berita_spreadsheet_id"],
                "worksheet_name": "DATASET BERITA"  # Adjust as needed
            }
        }
        
        if dataset_name not in dataset_map:
            raise ValueError(f"Dataset {dataset_name} tidak ditemukan")
        
        # Open the spreadsheet and worksheet
        spreadsheet = client.open_by_key(dataset_map[dataset_name]["spreadsheet_id"])
        worksheet = spreadsheet.worksheet(dataset_map[dataset_name]["worksheet_name"])
        
        # Convert to DataFrame
        data = worksheet.get_all_values()
        headers = data[0]
        df = pd.DataFrame(data[1:], columns=headers)
        
        return df
    
    except Exception as e:
        st.error(f"Gagal memuat dataset {dataset_name}: {e}")
        return pd.DataFrame()

def process_entities(df, column_name, separator=';'):
    """
    Process entities in a column
    
    Args:
        df (pd.DataFrame): Input dataframe
        column_name (str): Column with entities
        separator (str, optional): Separator for entities. Defaults to ';'.
    
    Returns:
        list: Processed unique entities
    """
    entities = df[column_name].dropna().str.split(separator).explode()
    return sorted(set(entities.str.strip()))

def get_unique_locations(df, column_name):
    """
    Get unique locations from a column
    
    Args:
        df (pd.DataFrame): Input dataframe
        column_name (str): Column with locations
    
    Returns:
        list: Sorted unique locations
    """
    locations = df[column_name].dropna().unique()
    return sorted(locations)
