"""
Code Executor Tool - Safely executes Python code for data analysis
"""

from langchain.tools import BaseTool
from typing import Optional, Dict, Any
import sys
import io
import traceback
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import warnings
warnings.filterwarnings('ignore')

class CodeExecutorTool(BaseTool):
    name: str = "Code Executor Tool"
    description: str = """Executes Python code for data analysis safely. The code has access to:
    - pandas (as pd)
    - numpy (as np) 
    - matplotlib.pyplot (as plt)
    - seaborn (as sns)
    - sklearn (various modules)
    
    Input: Python code to execute, optionally with dataset path"""
    
    def _create_safe_globals(self, dataset_path: Optional[str] = None) -> Dict[str, Any]:
        safe_globals = {
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'print': print,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'Path': Path,
            'os': os,
        }
        
        try:
            from sklearn import preprocessing, model_selection, linear_model
            from sklearn import tree, ensemble, metrics, cluster, decomposition
            safe_globals.update({
                'preprocessing': preprocessing,
                'model_selection': model_selection,
                'linear_model': linear_model,
                'tree': tree,
                'ensemble': ensemble,
                'metrics': metrics,
                'cluster': cluster,
                'decomposition': decomposition
            })
        except ImportError:
            pass
        
        if dataset_path and Path(dataset_path).exists():
            try:
                df = pd.read_csv(dataset_path)
                safe_globals['df'] = df
                safe_globals['dataset'] = df
            except Exception as e:
                print(f"Warning: Could not load dataset: {e}")
        
        return safe_globals
    
    def _run(self, code: str, dataset_path: Optional[str] = None) -> str:
        if not dataset_path and ',' in code:
            parts = code.split(',', 1)
            if len(parts) == 2:
                code = parts[0].strip()
                dataset_path = parts[1].strip().strip('"').strip("'")
        
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        safe_globals = self._create_safe_globals(dataset_path)
        
        output = []
        try:
            exec(code, safe_globals, safe_globals)
            
            output.append("=== CODE EXECUTION OUTPUT ===")
            printed_output = sys.stdout.getvalue()
            if printed_output:
                output.append(printed_output)
            
            figures = plt.get_fignums()
            if figures:
                output.append(f"\n=== VISUALIZATIONS CREATED ===")
                visuals_dir = Path('visuals')
                visuals_dir.mkdir(exist_ok=True)
                
                for i, fig_num in enumerate(figures):
                    fig = plt.figure(fig_num)
                    filename = f"figure_{len(list(visuals_dir.glob('*.png'))) + 1}.png"
                    filepath = visuals_dir / filename
                    fig.savefig(filepath, dpi=300, bbox_inches='tight')
                    output.append(f"- Saved: {filename}")
                    plt.close(fig)
            
            dataframes = {k: v for k, v in safe_globals.items() 
                         if isinstance(v, pd.DataFrame) and k not in ['df', 'dataset']}
            if dataframes:
                output.append("\n=== DATAFRAMES CREATED ===")
                for name, df in dataframes.items():
                    output.append(f"\n{name}: {df.shape[0]} rows × {df.shape[1]} columns")
                    if len(df) > 0:
                        output.append(df.head(3).to_string())
            
            result = "\n".join(output) if output else "Code executed successfully (no output)"
            return result
            
        except Exception as e:
            error_msg = f"Error executing code: {str(e)}\n"
            error_msg += f"Traceback:\n{traceback.format_exc()}"
            return error_msg
        
        finally:
            sys.stdout = old_stdout
            plt.close('all')