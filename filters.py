```python
import streamlit as st
import pandas as pd
from typing import List, Dict, Any

class DataFilterManager:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize filter manager with a DataFrame
        
        Args:
            df (pd.DataFrame): Source dataframe to filter
        """
        self.original_df = df.copy()
        self.current_df = df.copy()
        self.active_filters = {}
    
    def create_dynamic_filters(
        self, 
        columns: List[str] = None, 
        max_unique_values: int = 20
    ) -> Dict[str, Any]:
        """
        Generate dynamic filters based on column types
        
        Args:
            columns (List[str], optional): Columns to create filters for. Defaults to all columns.
            max_unique_values (int, optional): Max unique values to show in filter. Defaults to 20.
        
        Returns:
            Dict[str, Any]: Dictionary of interactive filter components
        """
        if columns is None:
            columns = self.original_df.columns
        
        filters = {}
        
        for col in columns:
            # Skip if column is not suitable for filtering
            if self.original_df[col].dtype == 'datetime64[ns]':
                filters[col] = self._create_date_range_filter(col)
            elif self.original_df[col].dtype == 'object':
                unique_values = self.original_df[col].dropna().unique()
                
                if len(unique_values) <= max_unique_values:
                    filters[col] = self._create_multiselect_filter(col, unique_values)
        
        return filters
    
    def _create_date_range_filter(self, column: str):
        """
        Create date range filter for a datetime column
        """
        min_date = self.original_df[column].min()
        max_date = self.original_df[column].max()
        
        return st.date_input(
            f"Filter {column}", 
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key=f"date_filter_{column}"
        )
    
    def _create_multiselect_filter(self, column: str, unique_values: List[str]):
        """
        Create multiselect filter for categorical columns
        """
        return st.multiselect(
            f"Filter {column}", 
            unique_values, 
            default=list(unique_values), 
            key=f"multiselect_filter_{column}"
        )
    
    def apply_filters(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply dynamic filters to the dataframe
        
        Args:
            filters (Dict[str, Any]): Dictionary of filter values
        
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        filtered_df = self.original_df.copy()
        
        for column, filter_value in filters.items():
            if column in self.original_df.columns:
                # Date range filter
                if isinstance(filter_value, tuple) and len(filter_value) == 2:
                    start_date, end_date = filter_value
                    filtered_df = filtered_df[
                        (filtered_df[column].dt.date >= start_date) & 
                        (filtered_df[column].dt.date <= end_date)
                    ]
                
                # Multiselect filter
                elif isinstance(filter_value, list):
                    filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
        
        return filtered_df
    
    def show_filter_summary(self, filtered_df: pd.DataFrame):
        """
        Display a summary of applied filters
        
        Args:
            filtered_df (pd.DataFrame): Filtered dataframe
        """
        total_original = len(self.original_df)
        total_filtered = len(filtered_df)
        
        with st.expander("📊 Filter Summary"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Data Awal", total_original)
            with col2:
                st.metric("Data Setelah Filter", total_filtered)
            
            percentage_filtered = (total_filtered / total_original) * 100
            st.progress(percentage_filtered / 100)
            st.caption(f"Tersaring: {percentage_filtered:.2f}%")

def create_advanced_filters(df: pd.DataFrame):
    """
    Create a comprehensive filter interface
    
    Args:
        df (pd.DataFrame): Source dataframe
    
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    st.sidebar.header("🔍 Filter Data")
    
    # Initialize filter manager
    filter_manager = DataFilterManager(df)
    
    # Create dynamic filters
    filters = filter_manager.create_dynamic_filters()
    
    # Apply filters
    filtered_df = filter_manager.apply_filters(
        {col: st.sidebar.session_state.get(f"multiselect_filter_{col}", filters[col]) 
         for col in filters}
    )
    
    # Show filter summary
    filter_manager.show_filter_summary(filtered_df)
    
    return filtered_df
```
