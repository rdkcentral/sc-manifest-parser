from setuptools import find_packages, setup

def read_version():
    with open("VERSION", "r") as f:
        return f.read().strip()

setup(
    name="sc_manifest_parser",
    version=read_version(),
    description="A library that parses repo manifests",
    packages=find_packages(),
    install_requires=[
        'lxml'
    ]
)