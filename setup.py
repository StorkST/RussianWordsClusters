import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RussianWordsClusters",
    version="0.0.7",
    author="Vincent Charrade",
    author_email="vchd@pm.me",
    description="Clustering russian words by multiple criterias",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StorkST/RussianWordsClusters/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
