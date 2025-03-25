import pandas as pd
import numpy as np
from typing import List, Dict, Any
import streamlit as st
from functools import lru_cache

class DataProcessor:
    def __init__(self, df: pd.DataFrame):
        """
        Inisialisasi processor dengan dataframe
        """
        self.df = df.copy()
        self.original_df = df.copy()
    
    @lru_cache(maxsize=32)
    def process_column(self, column_name: str, separator: str = ';') -> pd.Series:
        """
        Memproses kolom dengan entitas yang dipisahkan
        
        Args:
            column_name (str): Nama kolom yang akan diproses
            separator (str, optional): Pemisah entitas. Defaults to ';'.
        
        Returns:
            pd.Series: Series dengan entitas yang sudah diproses
        """
        if column_name not in self.df.columns:
            raise ValueError(f"Kolom {column_name} tidak ditemukan")
        
        def split_and_clean(value: str) -> List[str]:
            if pd.isna(value):
                return []
            
            # Split dan bersihkan
            entities = [entity.strip() for entity in str(value).split(separator)]
            
            # Filter entitas
            filtered = [
                entity for entity in entities 
                if entity and '##' not in entity
            ]
            
            return filtered
        
        return self.df[column_name].apply(split_and_clean)
    
    def aggregate_entities(
        self, 
        column_name: str, 
        top_n: int = 10, 
        min_count: int = 1
    ) -> pd.Series:
        """
        Agregasi entitas dengan perhitungan frekuensi
        
        Args:
            column_name (str): Nama kolom untuk agregasi
            top_n (int, optional): Jumlah top entitas. Defaults to 10.
            min_count (int, optional): Minimal kemunculan. Defaults to 1.
        
        Returns:
            pd.Series: Series frekuensi entitas
        """
        # Proses kolom
        processed_series = self.process_column(column_name)
        
        # Flatten list
        all_entities = [
            entity 
            for sublist in processed_series 
            for entity in sublist
        ]
        
        # Hitung frekuensi
        entity_counts = pd.Series(all_entities).value_counts()
        
        # Filter berdasarkan minimal count
        filtered_counts = entity_counts[entity_counts >= min_count]
        
        return filtered_counts.nlargest(top_n)
    
    def time_series_analysis(
        self, 
        date_column: str, 
        value_column: str = None, 
        resampling: str = 'M'
    ) -> pd.DataFrame:
        """
        Analisis deret waktu dengan resampling
        
        Args:
            date_column (str): Kolom tanggal
            value_column (str, optional): Kolom untuk agregasi. Defaults to None.
            resampling (str, optional): Periode resampling. Defaults to 'M'.
        
        Returns:
            pd.DataFrame: DataFrame dengan agregasi deret waktu
        """
        # Konversi ke datetime
        self.df[date_column] = pd.to_datetime(self.df[date_column], errors='coerce')
        
        # Set tanggal sebagai index
        df_time = self.df.set_index(date_column)
        
        if value_column:
            # Agregasi dengan kolom spesifik
            time_series = df_time.resample(resampling)[value_column].sum()
        else:
            # Agregasi jumlah baris
            time_series = df_time.resample(resampling).size()
        
        return time_series.reset_index()
    
    def correlation_analysis(
        self, 
        columns: List[str]
    ) -> pd.DataFrame:
        """
        Analisis korelasi antar kolom numerik
        
        Args:
            columns (List[str]): Daftar kolom untuk analisis korelasi
        
        Returns:
            pd.DataFrame: Matriks korelasi
        """
        # Filter kolom numerik
        numeric_df = self.df[columns].select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            raise ValueError("Tidak ada kolom numerik yang valid")
        
        return numeric_df.corr()
    
    def category_distribution(
        self, 
        column_name: str, 
        top_n: int = 10
    ) -> Dict[str, float]:
        """
        Distribusi kategori
        
        Args:
            column_name (str): Nama kolom kategori
            top_n (int, optional): Jumlah top kategori. Defaults to 10.
        
        Returns:
            Dict[str, float]: Distribusi persentase kategori
        """
        # Hitung distribusi
        value_counts = self.df[column_name].value_counts(normalize=True)
        top_categories = value_counts.nlargest(top_n)
        
        return top_categories.to_dict()

def cached_data_loader(func):
    """
    Decorator untuk caching load dataset
    """
    @lru_cache(maxsize=None)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@cached_data_loader
def load_and_process_dataset(dataset_name):
    """
    Load dan proses dataset dengan caching
    """
    # Implementasi load dataset yang sudah ada
    from data_loader import load_dataset
    
    df = load_dataset(dataset_name)
    
    if df.empty:
        st.warning(f"Dataset {dataset_name} kosong")
        return None
    
    return DataProcessor(df)

def data_insights(processor: DataProcessor):
    """
    Generate insights dari dataset
    
    Args:
        processor (DataProcessor): Instance DataProcessor
    
    Returns:
        Dict[str, Any]: Insights dari dataset
    """
    insights = {
        "total_rows": len(processor.df),
        "columns": list(processor.df.columns),
        "data_types": processor.df.dtypes.to_dict(),
        "missing_values": processor.df.isnull().sum().to_dict()
    }
    
    return insights
