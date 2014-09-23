#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'python-keystoneclient',
    'python-cinderclient',
    'python-novaclient',
]

setup(
    name='nectar-metrics',
    version='0.1.0',
    description='Metrics collection for the NeCTAR Research Cloud.',
    long_description=readme + '\n\n' + history,
    author='Russell Sim',
    author_email='russell.sim@gmail.com',
    url='https://github.com/NeCTAR-RC/nectar-metrics',
    packages=[
        'nectar_metrics',
    ],
    package_dir={'nectar_metrics': 'nectar_metrics'},
    include_package_data=True,
    install_requires=requirements,
    license="GPLv3+",
    zip_safe=False,
    keywords='nectar-metrics',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    data_files=[
        ('/etc/nectar', ['metrics.ini']),
    ],
    entry_points={
        'console_scripts':
        ['nectar-metrics-nova = nectar_metrics.nova:main',
         'nectar-metrics-cinder = nectar_metrics.cinder:main']
    },
)
