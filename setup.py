#!/usr/bin/env python3
"""
Setup script for AutoAnalyst
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autoanalyst",
    version="1.0.0",
    author="AutoAnalyst Team",
    author_email="",
    description="Autonomous AI Data Science Consultant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AutoAnalyst",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "crewai>=0.1.0",
        "pandas>=2.0.0",
        "seaborn>=0.12.0",
        "matplotlib>=3.7.0",
        "scikit-learn>=1.3.0",
        "reportlab>=4.0.0",
        "pypandoc>=1.11",
        "python-dotenv>=1.0.0",
        "autogen>=0.2.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "autoanalyst=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["prompts/*.txt", "datasets/*.csv"],
    },
)