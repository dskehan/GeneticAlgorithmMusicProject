"""Setup script for the Genetic Algorithm Music Project."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and ';' not in line:
            requirements.append(line)

setup(
    name="genetic-algorithm-music",
    version="1.0.0",
    description="A Python implementation of genetic algorithms for audio evolution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Genetic Music Team",
    author_email="contact@geneticmusic.com",
    url="https://github.com/yourusername/genetic-algorithm-music-python",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/genetic-algorithm-music-python/issues",
        "Documentation": "https://genetic-algorithm-music-python.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/genetic-algorithm-music-python",
    },
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    python_requires=">=3.8",
    install_requires=requirements,
    
    extras_require={
        "dev": [
            "black>=21.6.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "pre-commit>=2.13.0",
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "pytest-mock>=3.6.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "gui": [
            "tkinter-utils>=0.1.0",
        ],
        "viz": [
            "matplotlib>=3.5.0",
            "plotly>=5.0.0",
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    keywords=[
        "genetic-algorithm",
        "audio",
        "music",
        "evolution",
        "machine-learning",
        "sound-processing",
        "artificial-intelligence",
    ],
    
    entry_points={
        "console_scripts": [
            "genetic-music=genetic_music.cli:main",
            "genetic-music-gui=genetic_music.gui:main",
        ],
    },
    
    include_package_data=True,
    package_data={
        "genetic_music": [
            "config/*.toml",
            "gui/icons/*.png",
            "examples/*.py",
        ],
    },
    
    zip_safe=False,
)