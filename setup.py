#!/usr/bin/env python3
from setuptools import setup

setup(
    name='qfitswidget',
    version='0.8.2',
    description='PyQt widget for displaying FITS files',
    author='Tim-Oliver Husser',
    author_email='thusser@uni-goettingen.de',
    packages=['qfitswidget'],
    install_requires=[line.strip() for line in open("requirements.txt").readlines()]
)
