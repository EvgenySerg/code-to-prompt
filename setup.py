from setuptools import setup, find_packages
from pathlib import Path

# Read README.md if exists, otherwise use short description
def get_long_description():
    readme = Path("README.md")
    if readme.exists():
        return readme.read_text(encoding="utf-8")
    return "A tool to consolidate source code files for AI model prompts"

setup(
    name="src_consolidator",  # Changed from src-consolidator to src_consolidator
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to consolidate source code files for AI model prompts",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/src_consolidator",
    packages=find_packages(where="."),  # Explicitly specify where to find packages
    package_dir={"": "."},  # Add this line to specify package directory
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'src_consolidator=src_consolidator.cli:main',
        ],
    },
)