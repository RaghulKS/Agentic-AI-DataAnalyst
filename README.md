AutoAnalyst - Autonomous Data Science Consultant

An AI-powered autonomous data analyst that automatically analyzes datasets, generates insights, and creates professional business reports.

Overview

AutoAnalyst is an autonomous AI data consultant that ingests raw CSV datasets, infers analysis objectives, performs exploratory data analysis (EDA), creates visualizations, builds models, and generates comprehensive business-facing reports. It leverages CrewAI for multi-agent orchestration and GPT-4 for intelligent decision-making.

Features

- Autonomous Analysis: Automatically determines the best analysis approach for your data
- Comprehensive EDA: Performs thorough exploratory data analysis with visualizations
- Intelligent Modeling: Selects and applies appropriate statistical and ML models
- Professional Visualizations: Creates publication-ready charts and graphs
- Business Reports: Generates executive-ready PDF reports with insights and recommendations
- Multi-Agent System: Uses CrewAI for specialized AI agents (planning, coding, analysis, reporting)
- AutoGen Integration: Enhanced conversational AI and human-in-the-loop capabilities
- LangChain Tools: Sophisticated tool orchestration for complex analysis workflows
- Safe Execution: Sandboxed code execution environment for security
- Interactive Mode: Optional human-in-the-loop for guided analysis

Architecture

The system uses CrewAI to orchestrate four specialized agents:

1. Planner Agent: Analyzes dataset structure and creates analysis plans
2. Coder Agent: Converts plans into executable Python code
3. Analyst Agent: Executes code safely and collects results
4. Reporter Agent: Generates professional PDF reports

 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AutoAnalyst.git
cd AutoAnalyst
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up API keys:
```bash
cp secrets.example secrets.py
```
Edit `secrets.py` and add your OpenAI API key.

Usage

Basic Usage

Analyze a dataset with automatic analysis:
```bash
python main.py path/to/your/dataset.csv
```

With Specific Objective

Provide a specific analysis objective:
```bash
python main.py dataset.csv --objective "Identify factors affecting customer satisfaction"
```

Custom Output Name

Specify output report filename:
```bash
python main.py dataset.csv --output my_analysis_report.pdf
```

Advanced Usage

Enable AutoGen enhanced analysis (experimental):
```bash
python main.py dataset.csv --use-autogen --objective "Deep customer behavior analysis"
```

Interactive mode with human-in-the-loop:
```bash
python main.py dataset.csv --interactive
```

Verbose logging for debugging:
```bash
python main.py dataset.csv --verbose
```

Example

Using the included sample dataset:
```bash
python main.py datasets/sample_sales_data.csv --objective "Analyze sales patterns and customer behavior"
```

With AutoGen enhancement:
```bash
python main.py datasets/sample_sales_data.csv --use-autogen --objective "Advanced sales analysis with ML"
```

Output

AutoAnalyst generates:

- PDF Report in `reports/` directory
- Visualizations in `visuals/` directory
- Analysis Logs for debugging


Configuration

API Keys

Edit `config.py` to configure:
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: GPT model to use (default: gpt-4-turbo-preview)

Advanced Configuration

You can modify agent behaviors by editing the agent files in the `agents/` directory.

Supported Data Types

AutoAnalyst can analyze CSV files containing:
- Numerical data (integers, floats)
- Categorical data (strings)
- Date/time data
- Mixed data types

Example Reports

AutoAnalyst generates comprehensive reports including:
- Executive summary
- Data quality assessment
- Statistical analysis
- Visualizations with interpretations
- Machine learning model results
- Business recommendations

Troubleshooting

Common Issues

1. **API Key Error**: Ensure your OpenAI API key is correctly set in `config.py`
2. **Memory Error**: For large datasets, consider sampling or increasing system memory
3. **Missing Dependencies**: Run `pip install -r requirements.txt` again

Logs

Check the generated log files for detailed error information:
```
logs/autoanalyst_YYYYMMDD_HHMMSS.log
```

Testing

Run the comprehensive test suite to verify functionality:

```bash
python test_full_functionality.py
```

This will test:
- All dependencies and imports
- Agent and tool functionality  
- CrewAI integration
- AutoGen integration
- File structure and configuration
- Sample dataset validation

The test provides detailed feedback on any issues found.

Advanced Features

Web UI with Streamlit
Launch the web interface:
```bash
python run_streamlit.py
```
Access at: http://localhost:8501

API Endpoints
Start the API server:
```bash
python run_api.py
```
API documentation: http://localhost:8000/docs

Email Report Delivery
Configure email settings in `config.py`:
```python
SMTP_SERVER = "smtp.gmail.com"
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
```

Database Connectivity
Supports SQLite (default) and PostgreSQL:
```python
DATABASE_URL = "sqlite:///autoanalyst.db"
# or
DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

Real-time Data Analysis
Create real-time data streams via API:
```python
# POST /realtime/stream
# POST /realtime/data
# GET /realtime/analysis/{stream_id}
```
