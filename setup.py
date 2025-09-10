#!/usr/bin/env python3
"""
Setup script for DJ Mixer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dj-mixer",
    version="1.0.0",
    author="Jon Arve Ovesen",
    description="A Python-based DJ Mixer for playback on multiple sound devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GizzZmo/DJ",
    py_modules=[
        "dj_mixer",
        "dj_cli", 
        "test_mixer",
        "test_cli",
        "example"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Topic :: Multimedia :: Sound/Audio :: Mixers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dj-mixer=dj_cli:main",
            "dj-mixer-test=test_cli:main",
            "dj-mixer-example=example:main",
        ],
    },
    keywords="dj mixer audio music crossfading sound devices",
    project_urls={
        "Bug Reports": "https://github.com/GizzZmo/DJ/issues",
        "Source": "https://github.com/GizzZmo/DJ",
    },
)