from setuptools import setup, find_packages

setup(
    name="autofig",
    version="1.0.0-rc1",
    description="Network configuration generator for learning labs",
    author="Mizan",
    author_email="mizan@example.com",
    url="https://github.com/Dologara/Autofig",
    packages=find_packages(),
    python_requires=">=3.8",
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
