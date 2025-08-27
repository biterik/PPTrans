"""
Setup script for PPTrans
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
README = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

# Read requirements
REQUIREMENTS = (Path(__file__).parent / "requirements.txt").read_text().splitlines()

setup(
    name="pptrans",
    version="1.0.0",
    author="PPTrans Team",
    author_email="contact@pptrans.com",
    description="PowerPoint Translation Tool with format preservation",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/PPTrans",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/PPTrans/issues",
        "Documentation": "https://github.com/yourusername/PPTrans/docs",
        "Source Code": "https://github.com/yourusername/PPTrans",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "build": [
            "pyinstaller>=6.0.0",
            "setuptools-scm>=8.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "pptrans=main:main",
        ],
        "gui_scripts": [
            "pptrans-gui=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.json", "*.md", "*.txt"],
        "assets": ["*.png", "*.ico", "*.svg"],
    },
    zip_safe=False,
    keywords="powerpoint translation pptx google-translate office automation",
)