import codecs
import os

from setuptools import setup  # Always prefer setuptools over distutils

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with codecs.open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hunt_tools',
    version='0.0.1',
    description='ATS hunt tools',
    long_description=long_description,

    # Author details
    author='Darren Yin',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['tools'],

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [],
        'test': [],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            # 'setup_puzzle=sample:main',
        ],
    },
)
