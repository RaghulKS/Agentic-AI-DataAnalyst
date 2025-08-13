#!/usr/bin/env python3
"""
Example usage of AutoAnalyst
Demonstrates how to use the system programmatically
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import AutoAnalyst components
from agents.planner_agent import create_planner_agent
from agents.coder_agent import create_coder_agent
from agents.analyst_agent import create_analyst_agent
from agents.reporter_agent import create_reporter_agent
from tools.data_summary_tool import DataSummaryTool
from tools.code_executor_tool import CodeExecutorTool
from tools.visualization_tool import VisualizationTool
from tools.report_generator_tool import ReportGeneratorTool

def analyze_dataset(dataset_path, objective=None):
    """
    Example function showing how to use AutoAnalyst programmatically
    
    Args:
        dataset_path: Path to CSV dataset
        objective: Optional analysis objective
    """
    print(f"Starting analysis of {dataset_path}")
    
    # Initialize tools
    data_tool = DataSummaryTool()
    code_tool = CodeExecutorTool()
    viz_tool = VisualizationTool()
    report_tool = ReportGeneratorTool()
    
    # Get data summary
    print("\n1. Getting data summary...")
    summary = data_tool._run(dataset_path=dataset_path)
    print(summary[:500] + "...")  # Print first 500 chars
    
    # Example: Create a visualization
    print("\n2. Creating sample visualization...")
    import pandas as pd
    df = pd.read_csv(dataset_path)
    
    # If dataset has numeric columns, create a correlation heatmap
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        viz_result = viz_tool._run(
            plot_type="heatmap",
            data={"matrix": corr_matrix},
            title="Correlation Heatmap",
            save_name="correlation_heatmap.png"
        )
        print(viz_result)
    
    # Example: Execute some analysis code
    print("\n3. Running analysis code...")
    analysis_code = '''
import pandas as pd
import matplotlib.pyplot as plt

# Basic statistics
print("Dataset shape:", df.shape)
print("\\nColumn types:")
print(df.dtypes)

# Create a simple visualization
if 'Sales' in df.columns:
    plt.figure(figsize=(10, 6))
    df['Sales'].hist(bins=30, edgecolor='black')
    plt.title('Sales Distribution')
    plt.xlabel('Sales')
    plt.ylabel('Frequency')
    plt.savefig('visuals/sales_distribution.png')
    plt.close()
    print("\\nSales statistics:")
    print(df['Sales'].describe())
'''
    
    code_result = code_tool._run(code=analysis_code, dataset_path=dataset_path)
    print(code_result[:500] + "...")  # Print first 500 chars
    
    # Example: Generate a simple report
    print("\n4. Generating report...")
    report_content = f'''
# Data Analysis Report

## Executive Summary
This report presents the analysis of the dataset located at {dataset_path}.

## Data Overview
{summary[:1000]}

## Key Findings
- The dataset contains valuable information that can drive business decisions
- Further analysis reveals interesting patterns and relationships
- Statistical models can be applied to predict future outcomes

## Visualizations
![Correlation Heatmap](visuals/correlation_heatmap.png)

## Recommendations
1. Continue monitoring key metrics
2. Investigate anomalies further
3. Implement predictive models for forecasting
'''
    
    report_result = report_tool._run(
        content=report_content,
        title="AutoAnalyst Report",
        output_name="example_report.pdf"
    )
    print(report_result)
    
    print("\n✅ Analysis complete!")
    print("📊 Check the 'visuals' folder for generated charts")
    print("📄 Check the 'reports' folder for the PDF report")

if __name__ == "__main__":
    # Example 1: Analyze the sample dataset
    print("="*60)
    print("Example 1: Analyzing sample sales data")
    print("="*60)
    
    sample_dataset = "datasets/sample_sales_data.csv"
    if Path(sample_dataset).exists():
        analyze_dataset(sample_dataset, objective="Analyze sales patterns")
    else:
        print(f"Sample dataset not found at {sample_dataset}")
    
    # Example 2: Show how to use individual tools
    print("\n" + "="*60)
    print("Example 2: Using individual tools")
    print("="*60)
    
    # Create a simple visualization
    viz_tool = VisualizationTool()
    viz_result = viz_tool._run(
        plot_type="bar",
        data={
            "x": ["Product A", "Product B", "Product C", "Product D"],
            "y": [100, 150, 120, 180]
        },
        title="Product Sales Comparison",
        xlabel="Products",
        ylabel="Sales",
        save_name="product_comparison.png"
    )
    print(f"Visualization result: {viz_result}")
    
    print("\n🎉 Examples completed!")