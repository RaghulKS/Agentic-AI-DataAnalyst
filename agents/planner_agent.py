"""
Planner Agent - Analyzes dataset and creates comprehensive analysis plan
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def create_planner_agent():
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0.7
    )
    
    return Agent(
        role="Senior Data Scientist & Strategy Planner",
        goal="Analyze dataset structure and create comprehensive, actionable analysis plans",
        backstory="""You are a senior data scientist with 15+ years of experience in 
        data analysis, machine learning, and business intelligence. You excel at understanding 
        business problems, identifying patterns in data, and creating strategic analysis plans. 
        You have a keen eye for data quality issues and know exactly what analyses will provide 
        the most business value. You always consider the end user and ensure your plans lead 
        to actionable insights.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=3,
        memory=True,
        step_callback=None
    )