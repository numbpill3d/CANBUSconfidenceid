from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="can-hypothesis-engine",
    version="1.0.0",
    author="CAN Hypothesis Engine Team",
    author_email="contact@can-hypothesis.com",
    description="A tool for analyzing CAN bus logs to infer rolling counters, checksum bytes, and multi-byte numeric signals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/numbpill3d/CANBUSconfidenceid",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
    ],
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "can-hypothesis=can_hypothesis_engine.cli.main:main",
        ],
    },
    keywords="canbus can can-bus hypothesis rolling-counter checksum",
)