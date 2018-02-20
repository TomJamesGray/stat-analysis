import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Stat Analysis",
    version = "1.0",
    author = "Tom Gray",
    author_email = "tomg77@protonmail.com",
    description = (""),
    license = "BSD",
    keywords = "statisitcs",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['stat_analysis'],
    long_description=read('README.md'),
    include_package_data=True,
    scripts=["statanalysis.py"]
)
