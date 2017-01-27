from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
setup(
    name='atlas',
    version='0.0.1',
    packages=find_packages(),
    description='A class for easily accessing spatial and tabular data in a filesystem folder.',
    url='https://github.com/mjgleason/atlas',
    author='Mike Gleason',
    author_email='michael.gleason@digitialglobe.com',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'os',
        'sys',
        'shapely',
        'fiona',
        'rasterio',
        'fnmatch',
        'itertools',
        'geopandas',
        'pandas'
    ]
)