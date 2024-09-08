from setuptools import setup, find_packages

setup(
    name='repogather',
    version='0.0.3',
    description="Easily copy all relevant source files in a repository to clipboard",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'tiktoken',
        'pyperclip',
        'requests',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'repogather=repogather:main',
        ],
    },
    python_requires='>=3.7',
    license='MIT',
    include_package_data=True,
)