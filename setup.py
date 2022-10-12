"""Setup for the Python Project."""
import os
import re
import sys

from setuptools import setup


def get_version():
    """Get current version from code."""
    regex = r"__version__\s=\s\"(?P<version>[\d\.]+?)\""
    path = ("masterthermconnect", "__version__.py")
    return re.search(regex, read(*path)).group("version")


def read(*parts):
    """Read file."""
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)
    sys.stdout.write(filename)
    with open(filename, encoding="utf-8", mode="rt") as fptr:
        return fptr.read()


with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    author="Richard Holmes",
    author_email="richard@shedc.uk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    description="Python 3 API wrapper for MasterTherm API",
    name="masterthermconnect",
    keywords=["mastertherm heatpump", "api", "client"],
    license="MIT license",
    install_requires=["aiohttp"],
    long_description_content_type="text/markdown",
    long_description=readme,
    url="https://github.com/shedc/python-masterthermconnect",
    packages=["masterthermconnect"],
    version=get_version(),
)
