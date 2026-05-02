from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="feizhan",
    version="2.0.0",
    author="Feizhan Contributors",
    description="One-click website generator — 5 types x 10 styles x 12 features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luckychenxiaowen/feizhan",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "feizhan=feizhan:main",
        ],
    },
)
