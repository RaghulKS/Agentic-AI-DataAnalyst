#!/usr/bin/env python3
"""
Simple AutoAnalyst Demo
Demonstrates core functionality without complex dependencies
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import json

# Ensure directories exist
def setup_directories():
    """Create necessary directories"""
    dirs = ['reports', 'visuals', 'logs']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)

def analyze_dataset(csv_path):
    """
    Simple dataset analysis without external AI dependencies
    """
    print(f"🔍 Analyzing dataset: {csv_path}")
    
    # Load data
    df = pd.read_csv(csv_path)
    
    # Basic analysis
    analysis_results = {
        'dataset_info': {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        },
        'numeric_stats': {},
        'categorical_info': {},
        'insights': []
    }
    
    # Numeric column analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        analysis_results['numeric_stats'] = df[numeric_cols].describe().to_dict()
        
        # Create correlation heatmap
        if len(numeric_cols) > 1:
            plt.figure(figsize=(10, 8))
            corr_matrix = df[numeric_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('Correlation Matrix')
            plt.savefig('visuals/correlation_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
            analysis_results['insights'].append("Generated correlation heatmap")
    
    # Categorical column analysis
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        for col in categorical_cols[:3]:  # Limit to first 3
            value_counts = df[col].value_counts().head(10)
            analysis_results['categorical_info'][col] = value_counts.to_dict()
            
            # Create bar chart
            plt.figure(figsize=(10, 6))
            value_counts.plot(kind='bar')
            plt.title(f'Distribution of {col}')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'visuals/{col}_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            analysis_results['insights'].append(f"Generated distribution chart for {col}")
    
    # Additional visualizations for numeric data
    if len(numeric_cols) > 0:
        # Histograms
        for col in numeric_cols[:3]:  # Limit to first 3
            plt.figure(figsize=(8, 6))
            df[col].hist(bins=30, edgecolor='black')
            plt.title(f'Distribution of {col}')
            plt.xlabel(col)
            plt.ylabel('Frequency')
            plt.tight_layout()
            plt.savefig(f'visuals/{col}_histogram.png', dpi=300, bbox_inches='tight')
            plt.close()
            analysis_results['insights'].append(f"Generated histogram for {col}")
    
    return analysis_results

def generate_simple_report(analysis_results, dataset_name):
    """
    Generate a simple text report
    """
    report_content = []
    report_content.append("# AutoAnalyst Simple Analysis Report")
    report_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_content.append(f"Dataset: {dataset_name}")
    report_content.append("")
    
    # Dataset Overview
    info = analysis_results['dataset_info']
    report_content.append("## Dataset Overview")
    report_content.append(f"- **Shape**: {info['shape'][0]} rows × {info['shape'][1]} columns")
    report_content.append(f"- **Memory Usage**: {info['memory_usage_mb']} MB")
    report_content.append("")
    
    # Columns
    report_content.append("### Columns")
    for col, dtype in info['dtypes'].items():
        missing = info['missing_values'][col]
        missing_pct = (missing / info['shape'][0]) * 100
        report_content.append(f"- **{col}** ({dtype}): {missing} missing ({missing_pct:.1f}%)")
    report_content.append("")
    
    # Numeric Analysis
    if analysis_results['numeric_stats']:
        report_content.append("## Numeric Data Analysis")
        for col, stats in analysis_results['numeric_stats'].items():
            if isinstance(stats, dict) and 'mean' in stats:
                report_content.append(f"### {col}")
                report_content.append(f"- Mean: {stats['mean']:.2f}")
                report_content.append(f"- Std: {stats['std']:.2f}")
                report_content.append(f"- Min: {stats['min']:.2f}")
                report_content.append(f"- Max: {stats['max']:.2f}")
                report_content.append("")
    
    # Categorical Analysis
    if analysis_results['categorical_info']:
        report_content.append("## Categorical Data Analysis")
        for col, value_counts in analysis_results['categorical_info'].items():
            report_content.append(f"### {col}")
            report_content.append(f"Top values:")
            for value, count in list(value_counts.items())[:5]:
                pct = (count / info['shape'][0]) * 100
                report_content.append(f"- {value}: {count} ({pct:.1f}%)")
            report_content.append("")
    
    # Insights
    if analysis_results['insights']:
        report_content.append("## Generated Visualizations")
        for insight in analysis_results['insights']:
            report_content.append(f"- {insight}")
        report_content.append("")
    
    # Recommendations
    report_content.append("## Recommendations")
    report_content.append("1. Review the correlation matrix to identify relationships between variables")
    report_content.append("2. Check for outliers in the numeric distributions")
    report_content.append("3. Consider data cleaning for columns with high missing values")
    report_content.append("4. Explore categorical variables for potential insights")
    
    # Save report
    report_text = "\n".join(report_content)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"reports/simple_analysis_{timestamp}.txt"
    
    with open(report_path, 'w') as f:
        f.write(report_text)
    
    return report_path

def main():
    """
    Main function for simple demo
    """
    print("🚀 AutoAnalyst Simple Demo")
    print("=" * 50)
    
    # Setup
    setup_directories()
    
    # Check for sample dataset
    sample_path = "datasets/sample_sales_data.csv"
    if not Path(sample_path).exists():
        print(f"❌ Sample dataset not found: {sample_path}")
        print("Please ensure the sample dataset exists.")
        return
    
    # Run analysis
    try:
        results = analyze_dataset(sample_path)
        
        # Generate report
        report_path = generate_simple_report(results, "sample_sales_data.csv")
        
        # Summary
        print("\n✅ Analysis Complete!")
        print(f"📊 Dataset: {results['dataset_info']['shape'][0]} rows × {results['dataset_info']['shape'][1]} columns")
        print(f"📈 Visualizations: {len(results['insights'])} charts generated")
        print(f"📄 Report: {report_path}")
        print("\nGenerated files:")
        
        # List generated files
        for viz_file in Path('visuals').glob('*.png'):
            print(f"  📈 {viz_file}")
        
        print(f"  📄 {report_path}")
        
        print("\n🎉 Simple analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()