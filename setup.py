import setuptools

with open("README.md", "r", encoding="utf-8") as handle:
    long_description = handle.read()

setuptools.setup(
    name="m-notes",
    version="0.2.0",
    author="Matthew Jarvis",
    author_email="mattj23@gmail.com",
    description="Markdown note tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mattj23/m-notes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "PyYAML>=5.4.1",
        "click>=7.1.2",
        "python-dateutil>=2.8.1"
    ],
    entry_points={
        "console_scripts": [
            "mnote=mnotes.mnotes:main",
            # "mgo=mnotes.mnotes:mgo",
            "mdev=mnotes.dev.mdev:main"
        ]
    }
)