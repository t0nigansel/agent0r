from setuptools import find_packages, setup

setup(
    name="act0r",
    version="0.1.0",
    description="Local-first security testing tool for LLM agents",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=["pydantic>=2.7,<3.0", "PyYAML>=6.0,<7.0"],
    python_requires=">=3.9",
    entry_points={"console_scripts": ["act0r=act0r.cli:main"]},
)
