import os
import re
from setuptools import setup

def version():
    regex = r'^(?m){}[\s]*=[\s]*(?P<ver>\d*)$'

    with open(os.path.join(os.path.dirname(__file__), 'include.mk')) as f:
        ver = f.read()

    major = re.search(regex.format('MAJORVERSION'), ver).group('ver')
    minor = re.search(regex.format('MINORVERSION'), ver).group('ver')
    patch = re.search(regex.format('PATCHLEVEL'), ver).group('ver')
    return "{}.{}.{}".format(major, minor, patch)

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dcolumns',
    version=version(),
    packages=['dcolumn', 'dcolumn.dcolumns', 'dcolumn.dcolumns.migrations',
              'dcolumn.common',],
    include_package_data=True,
    license='MIT',
    description=('An app to give any Django database model the ability to '
                 'dynamically add fields.'),
    long_description=README,
    long_description_content_type='text/x-rst',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    keywords='Django DColumns',
    project_urls={'Source': 'https://github.com/cnobile2012/dcolumn'},
    install_requires=[
        'django',
        'dateutils',
        'python-dateutil',
        ],
    )
