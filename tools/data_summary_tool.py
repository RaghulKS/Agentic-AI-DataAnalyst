"""
Data Summary Tool - Provides comprehensive dataset summaries
"""

from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from pathlib import Path

class DataSummaryTool(BaseTool):
    name: str = "Data Summary Tool"
    description: str = """Provides comprehensive summary of a dataset including:
    - Shape and size
    - Column names and data types 
    - Missing values analysis
    - Basic statistics
    - Data quality issues
    
    Input: Path to CSV dataset file"""
    
    def _run(self, dataset_path: str) -> str:
        try:
            df = pd.read_csv(dataset_path)
            
            summary = []
            summary.append("=== DATASET SUMMARY ===\n")
            summary.append(f"File: {Path(dataset_path).name}")
            summary.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            summary.append(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")
            
            summary.append("=== COLUMN INFORMATION ===")
            col_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                missing = df[col].isnull().sum()
                missing_pct = (missing / len(df)) * 100
                unique = df[col].nunique()
                col_info.append(f"- {col}: {dtype}, {missing} missing ({missing_pct:.1f}%), {unique} unique values")
            summary.extend(col_info)
            summary.append("")
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary.append("=== NUMERIC COLUMNS STATISTICS ===")
                stats = df[numeric_cols].describe().round(2)
                summary.append(stats.to_string())
                summary.append("")
            
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                summary.append("=== CATEGORICAL COLUMNS ===")
                for col in categorical_cols[:5]:
                    value_counts = df[col].value_counts().head(5)
                    summary.append(f"\n{col} (top 5 values):")
                    for value, count in value_counts.items():
                        summary.append(f"  - {value}: {count} ({(count/len(df))*100:.1f}%)")
                if len(categorical_cols) > 5:
                    summary.append(f"\n... and {len(categorical_cols) - 5} more categorical columns")
                summary.append("")
            
            summary.append("=== DATA QUALITY ISSUES ===")
            issues = []
            
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                issues.append(f"- {duplicates} duplicate rows found")
            
            high_missing = []
            for col in df.columns:
                missing_pct = (df[col].isnull().sum() / len(df)) * 100
                if missing_pct > 50:
                    high_missing.append(f"{col} ({missing_pct:.1f}%)")
            if high_missing:
                issues.append(f"- High missing values in: {', '.join(high_missing)}")
            
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                if outliers > 0:
                    issues.append(f"- {outliers} potential outliers in {col}")
            
            if not issues:
                issues.append("- No major data quality issues detected")
            
            summary.extend(issues)
            
            return "\n".join(summary)
            
        except Exception as e:
            return f"Error analyzing dataset: {str(e)}"