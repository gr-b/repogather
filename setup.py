from setuptools import setup

setup(
    name='repocontextfilter',
    version='0.0.1',
    description="Filter relevant source files in a repository",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    py_modules=['repotokens'],
    install_requires=[
        'tiktoken',
    ],
    entry_points={
        'console_scripts': [
            'repotokens=repotokens:main',
        ],
    },
)