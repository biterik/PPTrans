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
    author="Erik Bitzek",
    author_email="erik.bitzek@fau.de",
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
    ],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "pptrans=main:main",
        ],
        "gui_scripts": [
            "pptrans-gui=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="powerpoint translation pptx google-translate office automation",
)