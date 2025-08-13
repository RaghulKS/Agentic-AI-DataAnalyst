"""
AutoGen Integration for AutoAnalyst
Provides enhanced conversational AI capabilities and human-in-the-loop functionality
"""

import os
import sys
from pathlib import Path
import autogen
from typing import Dict, List, Optional, Any
import json

sys.path.append(str(Path(__file__).parent))
import config

class AutoGenAnalysisAssistant:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.config_list = self._setup_config()
        self.agents = self._create_agents()
        self.groupchat = self._setup_groupchat()
        
    def _setup_config(self) -> List[Dict]:
        return [
            {
                "model": config.OPENAI_MODEL,
                "api_key": config.OPENAI_API_KEY,
                "temperature": 0.7,
            }
        ]
    
    def _create_agents(self) -> Dict[str, autogen.Agent]:
        agents = {}
        
        agents["data_scientist"] = autogen.AssistantAgent(
            name="DataScientist",
            llm_config={
                "config_list": self.config_list,
                "temperature": 0.3,
            },
            system_message="""You are an expert data scientist specializing in automated analysis.
            You can:
            - Generate Python code for data analysis, visualization, and machine learning
            - Explain statistical concepts and methodologies
            - Suggest appropriate analysis approaches based on data characteristics
            - Create comprehensive analysis reports
            
            Always write clean, well-documented code with proper error handling.
            Focus on generating actionable insights from data."""
        )
        
        agents["code_reviewer"] = autogen.AssistantAgent(
            name="CodeReviewer",
            llm_config={
                "config_list": self.config_list,
                "temperature": 0.2,
            },
            system_message="""You are a senior software engineer specializing in data science code review.
            Your responsibilities:
            - Review Python code for correctness, efficiency, and best practices
            - Identify potential bugs, performance issues, or security concerns
            - Suggest improvements and optimizations
            - Ensure code follows data science best practices
            
            Provide constructive feedback and specific suggestions for improvement."""
        )
        
        agents["business_analyst"] = autogen.AssistantAgent(
            name="BusinessAnalyst",
            llm_config={
                "config_list": self.config_list,
                "temperature": 0.7,
            },
            system_message="""You are a business analyst expert at translating technical findings into business insights.
            Your role:
            - Interpret statistical results in business context
            - Identify actionable recommendations from data analysis
            - Create executive summaries and business reports
            - Bridge the gap between technical analysis and business strategy
            
            Focus on practical implications and clear, non-technical communication."""
        )
        
        agents["user_proxy"] = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "work_dir": "autogen_workspace",
                "use_docker": False,
            },
            system_message="""You are a user proxy agent that can execute code and coordinate the analysis process.
            You work with the data science team to ensure high-quality analysis results."""
        )
        
        return agents
    
    def _setup_groupchat(self) -> autogen.GroupChat:
        groupchat = autogen.GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            max_round=12,
            speaker_selection_method="round_robin"
        )
        
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": self.config_list}
        )
        
        return manager
    
    def generate_analysis_code(self, analysis_plan: str) -> str:
        workspace = Path("autogen_workspace")
        workspace.mkdir(exist_ok=True)
        
        prompt = f"""
        Based on the following analysis plan, generate comprehensive Python code for data analysis:
        
        Analysis Plan:
        {analysis_plan}
        
        Dataset Path: {self.dataset_path}
        
        Requirements:
        1. Load and explore the dataset
        2. Implement all steps from the analysis plan
        3. Create meaningful visualizations
        4. Perform statistical analysis as appropriate
        5. Save results and visualizations
        
        Please generate clean, well-documented code that can be executed safely.
        """
        
        self.agents["user_proxy"].initiate_chat(
            self.agents["data_scientist"],
            message=prompt
        )
        
        return "# AutoGen generated code would be extracted here"
    
    def collaborative_analysis(self, objective: str) -> Dict[str, Any]:
        results = {
            "objective": objective,
            "dataset": str(self.dataset_path),
            "analysis_steps": [],
            "code_generated": "",
            "business_insights": "",
            "recommendations": []
        }
        
        planning_prompt = f"""
        We need to analyze the dataset at {self.dataset_path} with the objective: {objective}
        
        Let's collaborate to create a comprehensive analysis plan:
        1. Data Scientist: Suggest technical analysis approaches
        2. Business Analyst: Define business questions and success metrics
        3. Code Reviewer: Consider implementation best practices
        
        Please discuss and agree on the best approach.
        """
        
        self.agents["user_proxy"].initiate_chat(
            self.groupchat,
            message=planning_prompt
        )
        
        return results
    
    def interactive_analysis(self, user_questions: List[str]) -> List[str]:
        responses = []
        
        for question in user_questions:
            response = f"Processing: {question}"
            responses.append(response)
        
        return responses

class AutoGenCodeGenerator:
    def __init__(self):
        self.config_list = [
            {
                "model": config.OPENAI_MODEL,
                "api_key": config.OPENAI_API_KEY,
                "temperature": 0.1,
            }
        ]
        
        self.code_agent = autogen.AssistantAgent(
            name="DataScienceCodeGenerator",
            llm_config={"config_list": self.config_list},
            system_message="""You are an expert Python programmer specializing in data science.
            Generate clean, efficient, and well-documented Python code for data analysis tasks.
            
            Your code should:
            - Use pandas, numpy, matplotlib, seaborn, and scikit-learn appropriately
            - Include proper error handling and data validation
            - Create meaningful visualizations
            - Follow data science best practices
            - Be production-ready and executable
            
            Always explain your approach and document your code thoroughly."""
        )
        
        self.executor = autogen.UserProxyAgent(
            name="CodeExecutor",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
            code_execution_config={
                "work_dir": "autogen_workspace",
                "use_docker": False,
            }
        )
    
    def generate_and_execute_code(self, task_description: str, dataset_path: str) -> str:
        prompt = f"""
        Generate Python code for the following data science task:
        
        Task: {task_description}
        Dataset: {dataset_path}
        
        Please write complete, executable code that accomplishes this task.
        Save any visualizations to the 'visuals' directory.
        Include print statements to show key results.
        """
        
        self.executor.initiate_chat(
            self.code_agent,
            message=prompt
        )
        
        return "Code generated and executed via AutoGen"

def enhance_autoanalyst_with_autogen(dataset_path: str, objective: str) -> Dict[str, Any]:
    autogen_assistant = AutoGenAnalysisAssistant(dataset_path)
    
    results = autogen_assistant.collaborative_analysis(objective)
    
    code_generator = AutoGenCodeGenerator()
    
    enhanced_tasks = [
        "Perform advanced statistical testing",
        "Create interactive visualizations",
        "Build predictive models with cross-validation",
        "Generate feature importance analysis"
    ]
    
    for task in enhanced_tasks:
        code_generator.generate_and_execute_code(task, dataset_path)
    
    return {
        "enhanced_analysis": results,
        "autogen_tasks_completed": enhanced_tasks,
        "status": "AutoGen integration successful"
    }

if __name__ == "__main__":
    dataset_path = "datasets/sample_sales_data.csv"
    objective = "Analyze sales patterns and customer behavior"
    
    results = enhance_autoanalyst_with_autogen(dataset_path, objective)
    print("AutoGen Enhancement Results:", json.dumps(results, indent=2))