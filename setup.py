from setuptools import setup

# This call to setup() does all the work
setup(
    name="linelime",
    version="0.2.1 Beta",
    description="Get Line Timeline Data",
    author="Fadli Maulana M",
    author_email="wetmanz23@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["linelime"],
    include_package_data=True,
    install_requires=["requests"],
)