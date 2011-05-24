#!/usr/bin/env python

from setuptools import setup

setup(name='manysim',
      version='0.0,1',
      description='Perform Simulations on the Amazon Elastic Compute Cloud',
      long_description='manysim is a simple utility for executing arbitary \
                        code on EC2 using Python and the boto Python module. \
                        Jobs can be launched from the local user machine and \
                        executed on EC2 with results returned to the user via S3',
      author='Christopher M Poole',
      author_email='mail@christopherpoole.net',
      url='http://code.google.com/p/manysim/',
      py_modules=['manysim'],
      install_requires=['boto'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Apache Software License',],
     )
     
