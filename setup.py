from setuptools import setup, find_packages
from pathlib import Path
import re

# Single source of truth for the version: autofig/__init__.py
init_text = (Path(__file__).parent / "autofig" / "__init__.py").read_text()
version = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_text).group(1)

setup(
    name="autofig",
    version=version,
    description="Network configuration generator for learning labs",
    author="Mizan",
    author_email="mizan@example.com",
    url="https://github.com/Dologara/Autofig",
    packages=find_packages(),
    # loader.py/renderer.py use PEP 604 "X | Y" type hints, which require 3.10+.
    python_requires=">=3.10",
    install_requires=[
        "pyyaml>=6.0",
        "jinja2>=3.0",
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "autofig=autofig.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
