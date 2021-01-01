#!/usr/bin/env python3
from setuptools import setup

setup(
    name='qfitsview',
    version='0.5',
    description='PyQt widget for displaying FITS files',
    author='Tim-Oliver Husser',
    author_email='thusser@uni-goettingen.de',
    packages=['qfitsview'],
    install_requires=[
        'matplotlib',
        'PyQt5',
        'numpy',
        'astropy'
    ]
)
