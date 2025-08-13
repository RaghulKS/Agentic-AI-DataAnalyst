"""
Coder Agent - Converts analysis plans into executable Python code
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def create_coder_agent():
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0.3
    )
    
    return Agent(
        role="Expert Python Data Science Developer",
        goal="Transform analysis plans into clean, efficient, and executable Python code",
        backstory="""You are an expert Python programmer specializing in data science and analytics.
        You have deep expertise in pandas, numpy, scikit-learn, matplotlib, seaborn, and statistical analysis.
        You write production-quality code that is well-documented, efficient, and follows best practices. 
        You always include proper error handling, data validation, and clear comments. Your code is designed
        to be executed safely and produce meaningful insights. You understand both the technical implementation
        and the business context behind every analysis.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=3,
        memory=True,
        step_callback=None
    )