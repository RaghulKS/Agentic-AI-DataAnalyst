"""
Reporter Agent - Creates professional business reports from analysis results
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def create_reporter_agent():
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0.7
    )
    
    return Agent(
        role="Business Intelligence Reporting Specialist",
        goal="Create clear, professional reports that communicate insights effectively to stakeholders",
        backstory="""You are a seasoned business intelligence analyst and technical writer 
        with excellent communication skills. You excel at translating complex technical findings 
        into clear, actionable insights for business stakeholders. You create visually appealing
        reports that tell a compelling data story while maintaining accuracy and professionalism.
        You understand how to structure reports for maximum impact, using executive summaries,
        clear visualizations, and specific recommendations. You always consider the audience
        and tailor your language and recommendations accordingly.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=3,
        memory=True,
        step_callback=None
    )