#!/usr/bin/env python3

from pathlib import Path

from setuptools import find_packages, setup

readme_path = Path(__file__).parent / "README.md"
long_description = (
    readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
)

requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

dev_requirements_path = Path(__file__).parent / "requirements-dev.txt"
dev_requirements = []
if dev_requirements_path.exists():
    dev_requirements = [
        line.strip()
        for line in dev_requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="conduit-mcp",
    version="0.1.1",
    author="mcpnow.io",
    author_email="support@mcpnow.io",
    description="The MCP Server for Phabricator and Phorge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mcpnow-io/conduit",
    project_urls={
        "Bug Reports": "https://github.com/mcpnow-io/conduit/issues",
        "Source": "https://github.com/mcpnow-io/conduit",
        "Wiki": "https://github.com/mcpnow-io/conduit/wiki",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Bug Tracking",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": dev_requirements,
    },
    entry_points={
        "console_scripts": [
            "conduit-mcp=src.conduit:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="mcp phabricator phorge api client server automation",
)
