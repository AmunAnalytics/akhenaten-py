# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the version from the source code
with open(path.join(here, 'akhenaten', 'akhenaten.py'), encoding='utf-8') as f:
    lines = f.readlines()
    for l in lines:
        if l.startswith('__version__'):
            __version__ = l.split('"')[1] # take the part after the first "

setup(
    name='akhenaten-py',
    version=__version__,
    description='A python API wrapper for Akhenaten Plotly hoster',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AmunAnalytics/akhenaten-py',
    author='Frank Boerman',
    author_email='frank@amunanalytics.eu',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],

    keywords='Client for Akhenaten plotly hoster',

    packages=find_packages(),

    install_requires=['minio', 'pydantic[email]', 'plotly'],

    package_data={
        'akhenaten-py': ['LICENSE.md', 'README.md'],
    },
)
