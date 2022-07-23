# Local
from setuptools import setup, find_packages

# Project
from arbitrage_helper import PACKAGE_NAME, __version__


with open("README.md", "r") as file:
    LONG_DESCRIPTION = file.read()

setup(name=PACKAGE_NAME,
      version=__version__,
      install_requires=["selenium", "tqdm", "requests", "lxml", "python-decouple"],
      packages=find_packages())
