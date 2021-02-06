#!/usr/bin/env python3
from setuptools import setup

setup(
    name='qfitswidget',
    version='0.7.1',
    description='PyQt widget for displaying FITS files',
    author='Tim-Oliver Husser',
    author_email='thusser@uni-goettingen.de',
    packages=['qfitswidget'],
    install_requires=[
        'matplotlib',
        'PyQt5',
        'numpy',
        'astropy'
    ]
)
