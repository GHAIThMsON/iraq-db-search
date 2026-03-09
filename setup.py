from setuptools import setup, find_packages

setup(
    name='iraq-db-search',
    version='1.0.0',
    description='CLI tool to search Iraq database records',
    author='GHAIThMsON',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
    ],
    entry_points={
        'console_scripts': [
            'iraq-search=iraq_db_search.cli:cli',
        ],
    },
    python_requires='>=3.7',
)
