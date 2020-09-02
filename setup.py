import setuptools

with open("README.md", 'r') as fh:
    long_desc = fh.read()

setuptools.setup(
    name = "pinta-gmrt",
    version = "0.5.0",
    author = "Abhimanyu Susobhanan, Yogesh Maan, Bhal Chandra Joshi et al.",
    author_email = "abhisrkckl@gmail.com",
    description = "uGMRT Data Processing Pipeline",
    long_description = long_desc,
    long_description_content_type = "text/markdown",
    url = "https://github.com/abhisrkckl/pinta"
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
        "Topic :: Scientific/Engineering :: Astronomy"
    ],
    python_requires = '>=3.6',
)
