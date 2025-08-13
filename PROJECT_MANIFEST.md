# AutoAnalyst Project Manifest

This file lists all components of the AutoAnalyst project.

## Project Structure

```
AutoDataAnalyst/
│
├── agents/                    # AI Agent Modules
│   ├── __init__.py              # Package initialization
│   ├── planner_agent.py         # Plans analysis strategy
│   ├── coder_agent.py           # Writes analysis code
│   ├── analyst_agent.py         # Executes analysis
│   └── reporter_agent.py        # Creates reports
│
├── tools/                     # LangChain Tools
│   ├── __init__.py              # Package initialization
│   ├── data_summary_tool.py     # Dataset profiling
│   ├── code_executor_tool.py    # Safe code execution
│   ├── visualization_tool.py    # Chart generation
│   └── report_generator_tool.py # PDF report creation
│
├── prompts/                   # Agent Prompts
│   ├── planner_prompt.txt       # Planning instructions
│   └── reporter_prompt.txt      # Reporting instructions
│
├── datasets/                  # Input Data
│   └── sample_sales_data.csv    # Example dataset
│
├── reports/                   # Output Reports
│   └── (Generated PDF reports)
│
├── visuals/                   # Output Visualizations
│   └── (Generated charts/graphs)
│
├── Core Files
│   ├── main.py                  # Main application entry
│   ├── secrets.example          # API keys template
│   ├── requirements.txt         # Python dependencies
│   ├── setup.py                 # Package setup
│   ├── .gitignore              # Git ignore rules
│   ├── LICENSE                 # MIT License
│   └── README.md               # Project documentation
│
└── Utility Scripts
    ├── quickstart.bat          # Windows setup script
    ├── quickstart.sh           # Mac/Linux setup script
    ├── example_usage.py        # Usage examples
    └── test_installation.py    # Installation verifier
```

## Key Features

1. Multi-Agent System: Uses CrewAI to orchestrate specialized AI agents
2. Autonomous Analysis: Automatically determines analysis approach
3. Code Generation: Creates and executes analysis code
4. Professional Reports: Generates PDF reports with insights
5. Visualization: Creates publication-ready charts

## Setup Instructions

1. Copy `secrets.example` to `secrets.py`
2. Add your OpenAI API key to `secrets.py`
3. Run `pip install -r requirements.txt`
4. Execute `python main.py datasets/sample_sales_data.csv`

## API Keys Required

- OpenAI API Key: Required for GPT-4 access
- Other keys in `secrets.py` are optional for future features

## Usage

```bash
# Basic usage
python main.py path/to/dataset.csv

# With specific objective
python main.py dataset.csv --objective "Analyze customer behavior"

# Custom output name
python main.py dataset.csv --output custom_report.pdf
```

## Testing

Run `python test_installation.py` to verify your setup.

## Support

See README.md for detailed documentation and troubleshooting.