import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple-commons-uploader",
    version="0.3.3",
    author="Fastily",
    author_email="fastily@users.noreply.github.com",
    description="Batch Wikimedia Commons Uploader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastily/simple-commons-uploader",
    project_urls={
        "Bug Tracker": "https://github.com/fastily/simple-commons-uploader/issues",
    },
    include_package_data=True,
    packages=setuptools.find_packages(include=["scu"]),
    install_requires=['Pillow', 'pwiki', 'rich'],
    entry_points={
        'console_scripts': [
            'scu = scu.__main__:_main'
        ]
    },
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
