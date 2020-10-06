from setuptools import setup, find_packages
import gittools

with open("README.md", "r") as f:
    long_description = f.read()

setup(
        name='gittools',
        version=gittools.__version__,
        author='Olivier Vincent',
        author_email='olivier.vincent@univ-lyon1.fr',
        url='https://cameleon.univ-lyon1.fr/ovincent/gittools',
        description='Tools for git in python based on gitpython',
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
        ],
        setup_requires=['gitpython'],
        python_requires='>=3.6'
)
