from setuptools import setup

setup(
    name='repogather',
    version='0.0.1',
    description="Easily copy all relevant source files in a repository to clipboard",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    py_modules=['repogather'],
    install_requires=[
        'tiktoken',
    ],
    entry_points={
        'console_scripts': [
            'repogather=repogather:main',
        ],
    },
)