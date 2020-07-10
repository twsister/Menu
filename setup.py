import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gras",
    version="0.0.1",
    author="Jon Grasmeder",
    author_email="gras@github.com",
    description="Menu system for DFL",
    long_description="A menu system for DFL",
    long_description_content_type="text/markdown",
    url="https://github.com/twsister/Menu",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)