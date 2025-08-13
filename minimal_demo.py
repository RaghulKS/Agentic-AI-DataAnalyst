#!/usr/bin/env python3

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

def setup_directories():
    dirs = ['reports', 'visuals', 'logs']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)

def analyze_dataset_minimal(csv_path):
    print(f"🔍 Analyzing dataset: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    print(f"📊 Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")
    
    print("\n📋 Dataset Info:")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Data types: {df.dtypes.to_dict()}")
    print(f"  Missing values: {df.isnull().sum().to_dict()}")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print(f"\n📈 Numeric columns ({len(numeric_cols)}): {list(numeric_cols)}")
        print("  Basic statistics:")
        print(df[numeric_cols].describe())
        
        for col in numeric_cols[:2]:
            plt.figure(figsize=(8, 6))
            df[col].hist(bins=20, alpha=0.7, edgecolor='black')
            plt.title(f'Distribution of {col}')
            plt.xlabel(col)
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f'visuals/{col}_histogram.png', dpi=150, bbox_inches='tight')
            plt.close()
            print(f"  ✅ Created histogram for {col}")
    
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        print(f"\n📊 Categorical columns ({len(categorical_cols)}): {list(categorical_cols)}")
        
        for col in categorical_cols[:2]:
            value_counts = df[col].value_counts().head(10)
            print(f"  {col} - Top values: {dict(value_counts)}")
            
            plt.figure(figsize=(10, 6))
            value_counts.plot(kind='bar', color='skyblue', edgecolor='black')
            plt.title(f'Distribution of {col}')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f'visuals/{col}_distribution.png', dpi=150, bbox_inches='tight')
            plt.close()
            print(f"  ✅ Created bar chart for {col}")
    
    if len(numeric_cols) > 1:
        print(f"\n🔗 Correlation Analysis:")
        corr_matrix = df[numeric_cols].corr()
        print(corr_matrix)
        
        plt.figure(figsize=(10, 8))
        im = plt.imshow(corr_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
        plt.colorbar(im)
        plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45)
        plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
        plt.title('Correlation Matrix')
        
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                plt.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', 
                        ha='center', va='center', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('visuals/correlation_matrix.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✅ Created correlation matrix")
    
    return {
        'shape': df.shape,
        'columns': list(df.columns),
        'numeric_columns': list(numeric_cols),
        'categorical_columns': list(categorical_cols)
    }

def generate_minimal_report(analysis_info, dataset_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"reports/minimal_analysis_{timestamp}.txt"
    
    with open(report_path, 'w') as f:
        f.write("# AutoAnalyst Minimal Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dataset: {dataset_name}\n\n")
        
        f.write("## Dataset Overview\n")
        f.write(f"Shape: {analysis_info['shape'][0]} rows × {analysis_info['shape'][1]} columns\n\n")
        
        f.write("## Columns Analysis\n")
        f.write(f"Total columns: {len(analysis_info['columns'])}\n")
        f.write(f"Numeric columns: {len(analysis_info['numeric_columns'])}\n")
        f.write(f"Categorical columns: {len(analysis_info['categorical_columns'])}\n\n")
        
        if analysis_info['numeric_columns']:
            f.write("### Numeric Columns:\n")
            for col in analysis_info['numeric_columns']:
                f.write(f"- {col}\n")
            f.write("\n")
        
        if analysis_info['categorical_columns']:
            f.write("### Categorical Columns:\n")
            for col in analysis_info['categorical_columns']:
                f.write(f"- {col}\n")
            f.write("\n")
        
        f.write("## Generated Visualizations\n")
        f.write("Check the 'visuals' folder for:\n")
        f.write("- Histograms for numeric variables\n")
        f.write("- Bar charts for categorical variables\n")
        f.write("- Correlation matrix (if applicable)\n\n")
        
        f.write("## Next Steps\n")
        f.write("1. Review the generated visualizations\n")
        f.write("2. Look for patterns and outliers\n")
        f.write("3. Consider deeper analysis based on findings\n")
        f.write("4. Prepare data for modeling if needed\n")
    
    return report_path

def main():
    print("🚀 AutoAnalyst Minimal Demo")
    print("=" * 50)
    print("This demo uses only pandas and matplotlib")
    print("No external AI dependencies required!")
    print("")
    
    setup_directories()
    
    sample_path = "datasets/sample_sales_data.csv"
    if not Path(sample_path).exists():
        print(f"❌ Sample dataset not found: {sample_path}")
        
        print("📝 Creating sample dataset...")
        sample_data = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=50, freq='D'),
            'Product': np.random.choice(['Laptop', 'Phone', 'Tablet'], 50),
            'Category': np.random.choice(['Electronics', 'Accessories'], 50),
            'Sales': np.random.normal(1000, 200, 50),
            'Quantity': np.random.randint(1, 10, 50),
            'Region': np.random.choice(['North', 'South', 'East', 'West'], 50)
        })
        
        Path('datasets').mkdir(exist_ok=True)
        sample_data.to_csv(sample_path, index=False)
        print(f"✅ Created sample dataset: {sample_path}")
    
    try:
        analysis_info = analyze_dataset_minimal(sample_path)
        
        report_path = generate_minimal_report(analysis_info, "sample_sales_data.csv")
        
        print(f"\n✅ Analysis Complete!")
        print(f"📊 Dataset: {analysis_info['shape'][0]} rows × {analysis_info['shape'][1]} columns")
        print(f"📈 Numeric columns: {len(analysis_info['numeric_columns'])}")
        print(f"📊 Categorical columns: {len(analysis_info['categorical_columns'])}")
        print(f"📄 Report: {report_path}")
        
        print(f"\n📁 Generated files:")
        visuals = list(Path('visuals').glob('*.png'))
        for viz in visuals:
            print(f"  📈 {viz}")
        print(f"  📄 {report_path}")
        
        print(f"\n🎉 Minimal analysis completed successfully!")
        print(f"This demonstrates the core AutoAnalyst concept!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()