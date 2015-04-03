import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dcolumns',
    version='0.5.1',
    packages=['dcolumn', 'dcolumn.dcolumns', 'dcolumn.common',],
    include_package_data=True,
    license='MIT',
    description=('An app to give any Django database model the ability to '
                 'dynamically add fields.'),
    long_description=README,
    url='https://github.com/cnobile2012/dcolumn',
    author='Carl J. Nobile',
    author_email='carl.nobile@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    install_requires=[
        'python-dateutil',
        ],
    )
