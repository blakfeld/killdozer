#!/usr/bin/env python
from __future__ import absolute_import, print_function

import os
from setuptools import setup


def get_script_path():
    """
    Get the absolute path to this file.

    Returns:
        str
    """
    return os.path.abspath(os.path.dirname(__file__))


def get_long_description(readme_name='README.md'):
    """
    Get the long description text from our readme.

    Args:
        readme_name (str):  The name of the readme file.

    Returns:
        str
    """
    readme_fpath = os.path.join(get_script_path(), readme_name)
    if not os.path.isfile(readme_fpath):
        raise RuntimeError('ERROR: Unable to find README at path: {}'
                           .format(readme_fpath))

    with open(readme_fpath, 'r') as f:
        return f.read()


setup(
    name='killdozer',
    version='1.0.0',
    description='A Twitch Bot/GPIO Controller to control an RC Bulldozer.',
    long_description=get_long_description(),
    url='https://github.com/blakfeld/killdozer',
    author='Corwin Brown',
    author_email='corwin@corwinbrown.com',
    license='MIT',
    packages=['killdozer'],
    install_requires=[
        'pyyaml',
        'docopt',
        'RPi.GPIO'
    ],
    entry_points={
        'console_scripts': [
            'killdozer=killdozer.__main__:main',
        ],
    },
)
