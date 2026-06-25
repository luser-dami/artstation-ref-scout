#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="as-ref-scout",
    version="1.0.0",
    description="ArtStation art reference scouter - one-click search and collect art references",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "as-scout=as_ref_scout.crawl:main",
        ],
    },
    python_requires=">=3.8",
)
