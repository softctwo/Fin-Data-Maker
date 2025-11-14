from setuptools import setup, find_packages

setup(
    name="fin-data-maker",
    version="1.0.0",
    description="金融行业测试数据生成系统 - 用于生成符合监管报送要求的测试数据",
    author="Fin-Data-Maker Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "faker>=20.0.0",
        "pyyaml>=6.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "python-dateutil>=2.8.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
