#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='bndl_elastic',
    version='0.3.1',
    url='https://stash.tgho.nl/projects/THCLUSTER/repos/bndl_elastic/browse',
    description='Read from and write to Elastic Search with BNDL',
    long_description=open('README.md').read(),
    author='Frens Jan Rumph',
    author_email='mail@frensjan.nl',

    packages=(
        find_packages(exclude=["*.tests", "*.tests.*"])
    ),

    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'bndl>=0.3.0',
        'elasticsearch',
        'netifaces',
    ],

    extras_require=dict(
        dev=[
            'bndl[dev]',
        ],
    ),

    entry_points={
        'bndl.plugin':[
            'bndl_elastic=bndl_elastic',
        ]
    },

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
