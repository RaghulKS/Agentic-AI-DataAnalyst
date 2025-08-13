"""
Analyst Agent - Executes code and collects analysis results
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def create_analyst_agent():
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0.5
    )
    
    return Agent(
        role="Data Analysis Execution Specialist",
        goal="Execute analysis code safely, generate visualizations, and collect comprehensive results",
        backstory="""You are a meticulous data analyst who excels at running analyses
        and interpreting results. You have strong attention to detail and ensure that
        all code runs correctly, handling any errors gracefully. You are skilled at 
        creating meaningful visualizations and organizing outputs in a clear, accessible manner.
        You understand how to troubleshoot code issues and can suggest improvements.
        You always validate results and check for data quality issues during execution.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=5,
        memory=True,
        step_callback=None
    )