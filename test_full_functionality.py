#!/usr/bin/env python3
"""
Comprehensive test script for AutoAnalyst
Tests all components and integrations
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_config_configuration():
    """Test if config is properly configured"""
    print("🔐 Testing config configuration...")
    import config
    try:
        # Check if required keys exist
        required_keys = ['OPENAI_API_KEY', 'OPENAI_MODEL']
        missing_keys = []
        
        for key in required_keys:
            if not hasattr(config, key):
                missing_keys.append(key)
            elif getattr(config, key) in [None, "", "sk-your-openai-api-key-here"]:
                missing_keys.append(f"{key} (not configured)")
        
        if missing_keys:
            print(f"❌ Missing or unconfigured keys: {', '.join(missing_keys)}")
            return False
        
        print("✅ Config configuration looks good")
        return True
        
    except ImportError:
        print("❌ config.py not found")
        return False
    except Exception as e:
        print(f"❌ Error testing config: {e}")
        return False

def test_tool_imports():
    """Test importing all tools"""
    print("\n🔧 Testing tool imports...")
    try:
        from tools.data_summary_tool import DataSummaryTool
        from tools.code_executor_tool import CodeExecutorTool
        from tools.visualization_tool import VisualizationTool
        from tools.report_generator_tool import ReportGeneratorTool
        print("✅ All tools imported successfully")
        return True
    except Exception as e:
        print(f"❌ Tool import failed: {e}")
        traceback.print_exc()
        return False

def test_agent_imports():
    """Test importing all agents"""
    print("\n🤖 Testing agent imports...")
    try:
        from agents.planner_agent import create_planner_agent
        from agents.coder_agent import create_coder_agent
        from agents.analyst_agent import create_analyst_agent
        from agents.reporter_agent import create_reporter_agent
        print("✅ All agents imported successfully")
        return True
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        traceback.print_exc()
        return False

def test_crewai_integration():
    """Test CrewAI integration"""
    print("\n⚡ Testing CrewAI integration...")
    try:
        from crewai import Crew, Task, Process
        print("✅ CrewAI imported successfully")
        
        # Test agent creation
        from agents.planner_agent import create_planner_agent
        agent = create_planner_agent()
        print("✅ CrewAI agent creation successful")
        return True
    except Exception as e:
        print(f"❌ CrewAI integration failed: {e}")
        traceback.print_exc()
        return False

def test_autogen_integration():
    """Test AutoGen integration"""
    print("\n🔄 Testing AutoGen integration...")
    try:
        import autogen
        from autogen_integration import AutoGenAnalysisAssistant, AutoGenCodeGenerator
        print("✅ AutoGen imported successfully")
        return True
    except Exception as e:
        print(f"❌ AutoGen integration failed: {e}")
        traceback.print_exc()
        return False

def test_tool_functionality():
    """Test individual tool functionality"""
    print("\n🛠️ Testing tool functionality...")
    
    # Create test dataset
    test_data = pd.DataFrame({
        'id': range(1, 101),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'value': np.random.normal(100, 15, 100),
        'date': pd.date_range('2023-01-01', periods=100, freq='D')
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        test_data.to_csv(f.name, index=False)
        test_file = f.name
    
    try:
        # Test DataSummaryTool
        print("  📊 Testing DataSummaryTool...")
        from tools.data_summary_tool import DataSummaryTool
        data_tool = DataSummaryTool()
        summary = data_tool._run(test_file)
        assert "DATASET SUMMARY" in summary
        print("    ✅ DataSummaryTool working")
        
        # Test CodeExecutorTool
        print("  💻 Testing CodeExecutorTool...")
        from tools.code_executor_tool import CodeExecutorTool
        code_tool = CodeExecutorTool()
        test_code = """
import pandas as pd
print("Hello from CodeExecutorTool!")
print(f"Dataset shape: {df.shape}")
"""
        result = code_tool._run(test_code, test_file)
        assert "Hello from CodeExecutorTool!" in result
        print("    ✅ CodeExecutorTool working")
        
        # Test VisualizationTool
        print("  📈 Testing VisualizationTool...")
        from tools.visualization_tool import VisualizationTool
        viz_tool = VisualizationTool()
        viz_params = {
            'plot_type': 'bar',
            'data': {'x': ['A', 'B', 'C'], 'y': [10, 20, 15]},
            'title': 'Test Chart'
        }
        viz_result = viz_tool._run(str(viz_params))
        assert "successfully" in viz_result
        print("    ✅ VisualizationTool working")
        
        # Test ReportGeneratorTool
        print("  📄 Testing ReportGeneratorTool...")
        from tools.report_generator_tool import ReportGeneratorTool
        report_tool = ReportGeneratorTool()
        report_params = {
            'content': '# Test Report\n\nThis is a test.',
            'title': 'Test Report'
        }
        report_result = report_tool._run(str(report_params))
        assert "successfully" in report_result
        print("    ✅ ReportGeneratorTool working")
        
        print("✅ All tools functioning correctly")
        return True
        
    except Exception as e:
        print(f"❌ Tool functionality test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.unlink(test_file)

def test_sample_dataset():
    """Test the sample dataset"""
    print("\n📂 Testing sample dataset...")
    try:
        sample_path = Path('datasets/sample_sales_data.csv')
        if sample_path.exists():
            df = pd.read_csv(sample_path)
            print(f"  📊 Sample dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"  📋 Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
            print("✅ Sample dataset is valid")
            return True
        else:
            print("❌ Sample dataset not found")
            return False
    except Exception as e:
        print(f"❌ Sample dataset test failed: {e}")
        return False

def test_main_script():
    """Test the main script can be imported"""
    print("\n🚀 Testing main script import...")
    try:
        import main
        print("✅ Main script imports successfully")
        return True
    except Exception as e:
        print(f"❌ Main script import failed: {e}")
        traceback.print_exc()
        return False

def test_directory_structure():
    """Test project directory structure"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = ['agents', 'tools', 'prompts', 'datasets', 'reports', 'visuals']
    required_files = ['main.py', 'requirements.txt', 'README.md', 'config.example']
    
    missing_dirs = [d for d in required_dirs if not Path(d).exists()]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ Directory structure is correct")
    return True

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🧪 AutoAnalyst Comprehensive Functionality Test")
    print("=" * 60)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Config Configuration", test_config_configuration),
        ("Tool Imports", test_tool_imports),
        ("Agent Imports", test_agent_imports),
        ("CrewAI Integration", test_crewai_integration),
        ("AutoGen Integration", test_autogen_integration),
        ("Sample Dataset", test_sample_dataset),
        ("Tool Functionality", test_tool_functionality),
        ("Main Script", test_main_script),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
            if results[test_name]:
                passed += 1
        except Exception as e:
            results[test_name] = False
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! AutoAnalyst is fully functional.")
        print("\n🚀 Ready to run:")
        print("   python main.py datasets/sample_sales_data.csv")
        print("   python main.py datasets/sample_sales_data.csv --use-autogen")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Configure config.py with your OpenAI API key")
        print("3. Check that all directories and files exist")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)