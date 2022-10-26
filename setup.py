#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import sys

import os
from setuptools import setup, find_packages

import inginious

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

install_requires = [
    "docker==4.0.2",
    "docutils==0.16",
    "pymongo==3.9.0",
    "PyYAML==5.1",
    "web.py==0.40",
    "lti==0.9.4",
    "oauth2==1.9.0.post1",
    "httplib2==0.14.0",
    "watchdog == 0.9.0",
    "msgpack-python == 0.5.6",
    "pyzmq == 18.1.0",
    "natsort == 6.0.0",
    "psutil == 5.6.3",
    "zipstream == 1.1.4",
    "textdistance == 4.2.0",
]

test_requires = [
    "selenium==3.141.0",
    "nose",
    "pyvirtualdisplay"
]

# Platform specific dependencies
if not on_rtd:
    install_requires += ["pytidylib>=0.2.4", "sphinx-rtd-theme>=0.1.8"]
else:
    install_requires += test_requires + ["Pygments>=2.0.2"]

if sys.platform == 'win32':
    install_requires += ["pbs>=0.110"]
else:
    install_requires += ["sh>=1.11"]

# Setup
setup(
    name="INGInious",
    version=inginious.__version__,
    description="An intelligent grader that allows secured and automated testing of code made by students.",
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require={
        "cgi": ["flup>=1.0.3.dev"],
        "ldap": ["ldap3"],
        "saml2": ["python3-saml"],
        "uwsgi": ["uwsgi"],
        "test": test_requires
    },

    scripts=[
        'inginious-agent-docker',
        'inginious-agent-mcq',
        'inginious-backend',
        'inginious-webapp',
        'inginious-install',
        'utils/sync/inginious-synchronize',
        'utils/container_update/inginious-container-update',
        'utils/database_updater/inginious-database-update'
    ],

    include_package_data=True,
    test_suite='nose.collector',
    author="INGInious contributors",
    author_email="inginious@info.ucl.ac.be",
    license="AGPL 3",
    url="https://github.com/JuezUN/INGInious",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf8').read()
)
