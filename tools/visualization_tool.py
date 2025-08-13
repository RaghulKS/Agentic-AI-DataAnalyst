"""
Visualization Tool - Creates and saves data visualizations
"""

from langchain.tools import BaseTool
from typing import Optional, List, Dict, Any
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

class VisualizationTool(BaseTool):
    name: str = "Visualization Tool"
    description: str = """Creates professional data visualizations and saves them as PNG files. 
    
    Input format: JSON string with keys:
    - plot_type: bar, line, scatter, heatmap, box, violin, hist, pie
    - data: dictionary containing plot data
    - title: plot title
    - xlabel: x-axis label (optional)
    - ylabel: y-axis label (optional)
    - save_name: filename (optional)
    
    Example: {"plot_type": "bar", "data": {"x": [1,2,3], "y": [10,20,30]}, "title": "Sample Chart"}"""
    
    def _run(self, visualization_params: str) -> str:
        try:
            if isinstance(visualization_params, str):
                try:
                    params = json.loads(visualization_params)
                except json.JSONDecodeError:
                    return "Error: Please provide visualization parameters as valid JSON"
            else:
                params = visualization_params
            
            plot_type = params.get('plot_type', 'bar')
            data = params.get('data', {})
            title = params.get('title', 'Chart')
            xlabel = params.get('xlabel', '')
            ylabel = params.get('ylabel', '')
            save_name = params.get('save_name', None)
            
            sns.set_style("whitegrid")
            plt.figure(figsize=(10, 6))
            
            if plot_type == "bar":
                if 'x' in data and 'y' in data:
                    plt.bar(data['x'], data['y'])
                else:
                    return "Error: Bar plot requires 'x' and 'y' in data"
            
            elif plot_type == "line":
                if 'x' in data and 'y' in data:
                    plt.plot(data['x'], data['y'], marker='o')
                else:
                    return "Error: Line plot requires 'x' and 'y' in data"
            
            elif plot_type == "scatter":
                if 'x' in data and 'y' in data:
                    plt.scatter(data['x'], data['y'], alpha=0.6)
                else:
                    return "Error: Scatter plot requires 'x' and 'y' in data"
            
            elif plot_type == "heatmap":
                if 'matrix' in data:
                    matrix = data['matrix']
                    if isinstance(matrix, pd.DataFrame):
                        sns.heatmap(matrix, annot=True, cmap='coolwarm', center=0)
                    else:
                        sns.heatmap(np.array(matrix), annot=True, cmap='coolwarm', center=0)
                else:
                    return "Error: Heatmap requires 'matrix' in data"
            
            elif plot_type == "box":
                if 'data' in data:
                    plot_data = data['data']
                    if isinstance(plot_data, pd.DataFrame):
                        plot_data.boxplot()
                    elif isinstance(plot_data, list):
                        plt.boxplot(plot_data)
                    else:
                        plt.boxplot([plot_data])
                else:
                    return "Error: Box plot requires 'data' in data"
            
            elif plot_type == "violin":
                if 'data' in data:
                    plot_data = data['data']
                    if isinstance(plot_data, pd.DataFrame):
                        for i, col in enumerate(plot_data.columns):
                            plt.violinplot(plot_data[col].dropna(), positions=[i])
                        plt.xticks(range(len(plot_data.columns)), plot_data.columns)
                    else:
                        plt.violinplot(plot_data)
                else:
                    return "Error: Violin plot requires 'data' in data"
            
            elif plot_type == "hist":
                if 'data' in data:
                    plot_data = data['data']
                    bins = data.get('bins', 30)
                    plt.hist(plot_data, bins=bins, alpha=0.7, edgecolor='black')
                else:
                    return "Error: Histogram requires 'data' in data"
            
            elif plot_type == "pie":
                if 'values' in data and 'labels' in data:
                    plt.pie(data['values'], labels=data['labels'], autopct='%1.1f%%')
                else:
                    return "Error: Pie chart requires 'values' and 'labels' in data"
            
            else:
                return f"Error: Unknown plot type '{plot_type}'"
            
            plt.title(title, fontsize=14, fontweight='bold')
            if xlabel and plot_type != 'pie':
                plt.xlabel(xlabel, fontsize=12)
            if ylabel and plot_type != 'pie':
                plt.ylabel(ylabel, fontsize=12)
            
            visuals_dir = Path('visuals')
            visuals_dir.mkdir(exist_ok=True)
            
            if not save_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = f"{plot_type}_{timestamp}.png"
            
            if not save_name.endswith('.png'):
                save_name += '.png'
            
            filepath = visuals_dir / save_name
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return f"Visualization saved successfully: {save_name} in visuals/ directory"
            
        except Exception as e:
            plt.close()
            return f"Error creating visualization: {str(e)}"