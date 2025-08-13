#!/usr/bin/env python3
"""
AutoAnalyst - Autonomous Data Science Consultant
Main entry point for the application
"""

import os
import sys
from pathlib import Path
import argparse
import logging
from datetime import datetime
import traceback

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    import config
except ImportError:
    print("Error: config.py not found. Please copy config.example to config.py and add your API keys.")
    sys.exit(1)

from crewai import Crew, Task, Process
from agents.planner_agent import create_planner_agent
from agents.coder_agent import create_coder_agent
from agents.analyst_agent import create_analyst_agent
from agents.reporter_agent import create_reporter_agent
from tools.data_summary_tool import DataSummaryTool
from tools.code_executor_tool import CodeExecutorTool
from tools.visualization_tool import VisualizationTool
from tools.report_generator_tool import ReportGeneratorTool
from autogen_integration import enhance_autoanalyst_with_autogen

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f'autoanalyst_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def setup_directories():
    """Ensure all required directories exist"""
    directories = ['datasets', 'reports', 'visuals', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def validate_dataset(dataset_path):
    """Validate that the dataset exists and is readable"""
    if not Path(dataset_path).exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    # Try to read the first few lines to validate it's a proper CSV
    try:
        import pandas as pd
        df = pd.read_csv(dataset_path, nrows=5)
        if len(df.columns) == 0:
            raise ValueError("Dataset appears to be empty or malformed")
        return True
    except Exception as e:
        raise ValueError(f"Dataset validation failed: {str(e)}")

class AutoAnalyst:
    """Main AutoAnalyst class for orchestrating the analysis"""
    
    def __init__(self, dataset_path, objective=None, output_name=None):
        self.dataset_path = Path(dataset_path)
        self.objective = objective or "Comprehensive data analysis to uncover insights and patterns"
        self.output_name = output_name
        self.logger = logging.getLogger(__name__)
        
        # Initialize tools
        self.data_summary_tool = DataSummaryTool()
        self.code_executor_tool = CodeExecutorTool()
        self.visualization_tool = VisualizationTool()
        self.report_generator_tool = ReportGeneratorTool()
        
        # Initialize agents
        self.planner = create_planner_agent()
        self.coder = create_coder_agent()
        self.analyst = create_analyst_agent()
        self.reporter = create_reporter_agent()
        
        # Assign tools to agents
        self.planner.tools = [self.data_summary_tool]
        self.coder.tools = []  # Coder doesn't need tools, just generates code
        self.analyst.tools = [self.code_executor_tool, self.visualization_tool]
        self.reporter.tools = [self.report_generator_tool]
    
    def create_tasks(self):
        """Create the analysis tasks for the crew"""
        
        # Task 1: Planning and Data Analysis
        planning_task = Task(
            description=f"""
            Analyze the dataset at {self.dataset_path} and create a comprehensive analysis plan.
            
            Objective: {self.objective}
            
            Your task:
            1. Use the data summary tool to understand the dataset structure, quality, and characteristics
            2. Identify the most important questions this data can answer
            3. Create a detailed analysis plan including:
               - Data cleaning and preprocessing steps needed
               - Key exploratory data analysis (EDA) to perform
               - Appropriate statistical analyses or machine learning models
               - Specific visualizations that would provide insights
               - Business questions that can be answered
            
            Output a clear, structured analysis plan that the coding agent can implement.
            """,
            agent=self.planner,
            tools=[self.data_summary_tool],
            expected_output="A comprehensive analysis plan with specific steps for data cleaning, EDA, modeling, and visualization"
        )
        
        # Task 2: Code Generation
        coding_task = Task(
            description="""
            Based on the analysis plan, write comprehensive Python code to execute the analysis.
            
            Your task:
            1. Write clean, well-documented Python code that implements the analysis plan
            2. Include data loading, cleaning, and preprocessing
            3. Create meaningful visualizations using matplotlib/seaborn
            4. Perform statistical analysis and/or machine learning as appropriate
            5. Ensure all code is production-ready with error handling
            6. Structure the code in logical sections with clear comments
            
            The code will be executed by the analyst agent, so make sure it's complete and runnable.
            Assume pandas is available as 'pd', numpy as 'np', matplotlib.pyplot as 'plt', and seaborn as 'sns'.
            The dataset will be available as 'df' when the code runs.
            """,
            agent=self.coder,
            context=[planning_task],
            expected_output="Complete, executable Python code that implements the analysis plan"
        )
        
        # Task 3: Code Execution and Analysis
        execution_task = Task(
            description=f"""
            Execute the provided Python code and collect comprehensive results.
            
            Your task:
            1. Execute the analysis code using the code executor tool
            2. Pass the dataset path: {self.dataset_path}
            3. Create visualizations using the visualization tool as needed
            4. Collect and organize all outputs including:
               - Statistical results and findings
               - Generated visualizations and their interpretations
               - Data quality assessments
               - Model performance metrics (if applicable)
               - Key insights discovered
            
            Handle any errors gracefully and provide alternative approaches if needed.
            Document all findings clearly for the reporting agent.
            """,
            agent=self.analyst,
            tools=[self.code_executor_tool, self.visualization_tool],
            context=[coding_task],
            expected_output="Comprehensive analysis results including executed code outputs, visualizations, and key findings"
        )
        
        # Task 4: Report Generation
        reporting_task = Task(
            description=f"""
            Create a professional business report based on all analysis results.
            
            Your task:
            1. Synthesize all findings from the analysis into a cohesive business report
            2. Structure the report with:
               - Executive Summary with key insights
               - Data Overview and Quality Assessment
               - Methodology and Analysis Approach
               - Key Findings with supporting visualizations
               - Statistical Results and Interpretations
               - Business Implications and Recommendations
               - Limitations and Future Considerations
            
            3. Use the report generator tool to create a professional PDF
            4. Write in business language suitable for executives and stakeholders
            5. Focus on actionable insights and clear recommendations
            
            Output filename: {self.output_name or 'autoanalyst_report.pdf'}
            """,
            agent=self.reporter,
            tools=[self.report_generator_tool],
            context=[planning_task, execution_task],
            expected_output="A professional PDF report with executive summary, findings, and business recommendations"
        )
        
        return [planning_task, coding_task, execution_task, reporting_task]
    
    def run_analysis(self):
        """Execute the full analysis workflow"""
        try:
            self.logger.info(f"Starting AutoAnalyst analysis of {self.dataset_path}")
            self.logger.info(f"Objective: {self.objective}")
            
            # Create tasks
            tasks = self.create_tasks()
            
            # Create and configure the crew
            crew = Crew(
                agents=[self.planner, self.coder, self.analyst, self.reporter],
                tasks=tasks,
                process=Process.sequential,
                memory=True,
                verbose=True,
                embedder={
                    "provider": "openai",
                    "config": {
                        "api_key": config.OPENAI_API_KEY,
                        "model": "text-embedding-ada-002"
                    }
                }
            )
            
            self.logger.info("Starting crew execution...")
            
            # Execute the crew
            result = crew.kickoff()
            
            # Generate output summary
            self.generate_completion_summary()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {str(e)}", exc_info=True)
            raise
    
    def generate_completion_summary(self):
        """Generate a summary of completed analysis"""
        reports_dir = Path('reports')
        visuals_dir = Path('visuals')
        
        # Count generated files
        reports = list(reports_dir.glob('*.pdf'))
        visuals = list(visuals_dir.glob('*.png'))
        
        # Generate output filename if not provided
        if not self.output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dataset_name = self.dataset_path.stem
            self.output_name = f"analysis_{dataset_name}_{timestamp}.pdf"
        
        print(f"\n{'='*80}")
        print(f"🎉 AutoAnalyst Analysis Complete!")
        print(f"{'='*80}")
        print(f"📊 Dataset Analyzed: {self.dataset_path}")
        print(f"🎯 Objective: {self.objective}")
        print(f"📄 Reports Generated: {len(reports)} files in reports/")
        print(f"📈 Visualizations Created: {len(visuals)} files in visuals/")
        print(f"📝 Logs Available: logs/")
        print(f"{'='*80}")
        
        if reports:
            print("📄 Generated Reports:")
            for report in reports[-3:]:  # Show last 3 reports
                print(f"   - {report.name}")
        
        if visuals:
            print("📈 Generated Visualizations:")
            for visual in visuals[-5:]:  # Show last 5 visuals
                print(f"   - {visual.name}")
        
        print(f"\n🚀 Your autonomous data analysis is complete!")
        print(f"Check the reports/ directory for your business-ready insights.")
        print(f"{'='*80}\n")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='AutoAnalyst - Autonomous Data Science Consultant')
    parser.add_argument('dataset', type=str, help='Path to the CSV dataset to analyze')
    parser.add_argument('--objective', type=str, default=None, 
                       help='Specific analysis objective (default: comprehensive analysis)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output report filename (default: auto-generated)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--use-autogen', action='store_true',
                       help='Enable AutoGen enhanced analysis (experimental)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Enable interactive mode with human-in-the-loop')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Setup directories
        setup_directories()
        
        # Validate dataset
        validate_dataset(args.dataset)
        
        # Copy dataset to datasets folder if not already there
        dataset_path = Path(args.dataset)
        if dataset_path.parent != Path('datasets'):
            import shutil
            new_path = Path('datasets') / dataset_path.name
            shutil.copy2(dataset_path, new_path)
            dataset_path = new_path
            logger.info(f"Copied dataset to {dataset_path}")
        
        # Create and run AutoAnalyst
        analyst = AutoAnalyst(
            dataset_path=dataset_path,
            objective=args.objective,
            output_name=args.output
        )
        
        result = analyst.run_analysis()
        
        # Optional AutoGen enhancement
        if args.use_autogen:
            logger.info("Running AutoGen enhanced analysis...")
            try:
                autogen_results = enhance_autoanalyst_with_autogen(
                    str(dataset_path), 
                    args.objective or "Comprehensive data analysis"
                )
                logger.info("AutoGen enhancement completed successfully!")
            except Exception as e:
                logger.warning(f"AutoGen enhancement failed: {str(e)}")
        
        logger.info("AutoAnalyst completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()