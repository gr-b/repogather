from setuptools import setup

setup(
    name='repogather',
    version='0.0.1',
    description="Easily copy all relevant source files in a repository to clipboard",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    py_modules=['repogather'],
    url="https://github.com/gr-b/repogather",
    install_requires=[
        "requests",
        "python-dotenv",
        "pyperclip",
        "tiktoken",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)