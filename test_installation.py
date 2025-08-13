#!/usr/bin/env python3

import sys
import importlib
from pathlib import Path

def test_imports():
    print("Testing imports...")
    
    required_modules = [
        ('openai', 'OpenAI API'),
        ('langchain', 'LangChain'),
        ('crewai', 'CrewAI'),
        ('pandas', 'Pandas'),
        ('seaborn', 'Seaborn'),
        ('matplotlib', 'Matplotlib'),
        ('sklearn', 'Scikit-learn'),
        ('reportlab', 'ReportLab'),
        ('numpy', 'NumPy'),
    ]
    
    all_good = True
    for module_name, display_name in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {display_name} - OK")
        except ImportError as e:
            print(f"❌ {display_name} - FAILED: {e}")
            all_good = False
    
    return all_good

def test_project_structure():
    print("\nTesting project structure...")
    
    required_dirs = ['agents', 'tools', 'prompts', 'datasets', 'reports', 'visuals']
    required_files = ['main.py', 'requirements.txt', 'README.md']
    
    all_good = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ Directory '{dir_name}' - OK")
        else:
            print(f"❌ Directory '{dir_name}' - MISSING")
            all_good = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ File '{file_name}' - OK")
        else:
            print(f"❌ File '{file_name}' - MISSING")
            all_good = False
    
    return all_good

def test_config():
    print("\nTesting configuration...")
    
    try:
        import config
        if hasattr(config, 'OPENAI_API_KEY'):
            if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "sk-your-openai-api-key-here":
                print("✅ OpenAI API key is configured")
                return True
            else:
                print("⚠️  OpenAI API key is not configured")
                print("   Please edit config.py and add your actual API key")
                return False
        else:
            print("❌ OPENAI_API_KEY not found in config.py")
            return False
    except ImportError:
        print("❌ config.py not found")
        print("   Please copy config.example to config.py and configure it")
        return False

def test_sample_data():
    print("\nTesting sample data...")
    
    sample_file = Path('datasets/sample_sales_data.csv')
    if sample_file.exists():
        print(f"✅ Sample dataset exists: {sample_file}")
        return True
    else:
        print(f"❌ Sample dataset not found: {sample_file}")
        return False

def main():
    print("="*60)
    print("AutoAnalyst Installation Test")
    print("="*60)
    
    tests = [
        ("Dependencies", test_imports),
        ("Project Structure", test_project_structure),
        ("Configuration", test_config),
        ("Sample Data", test_sample_data),
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        emoji = "✅" if passed else "❌"
        print(f"{emoji} {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All tests passed! AutoAnalyst is ready to use.")
        print("\nRun the following command to analyze the sample dataset:")
        print("  python main.py datasets/sample_sales_data.csv")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Copy config.example to config.py and add your API key")
        print("3. Ensure all directories exist")
    print("="*60)

if __name__ == "__main__":
    main()