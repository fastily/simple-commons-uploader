import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple-commons-uploader",
    version="0.1.1",
    author="Fastily",
    author_email="fastily@users.noreply.github.com",
    description="Batch Wikimedia Commons Uploader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastily/simple-commons-uploader",
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'scu = simple_commons_uploader.scu:main'
        ]
    },
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)