#!/usr/bin/env python

import os

from setuptools import setup, find_packages


def file_content(filename):
    '''Load file content'''
    with open(filename) as ifile:
        return ifile.read()


def get_requirements():
    '''Return content of pip requirement file and add udata'''
    # unpinned udata requirement
    reqs = ['udata']
    reqs += file_content(os.path.join('requirements', 'install.pip')).splitlines()
    return reqs


long_description = '\n'.join((
    file_content('README.md'),
    file_content('CHANGELOG.md'),
    ''
))

setup(
    name='udata-front',
    version=__import__('udata_front').__version__,
    description=__import__('udata_front').__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/amagovpt/udata-front-pt',
    author='AMA - Agência para a Modernização Administrativa',
    author_email='ama@ama.pt',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=get_requirements(),
    entry_points={
        'udata.themes': [
            'gouvfr = udata_front.theme.gouvfr',
        ],
        'udata.models': [
            'front = udata_front.models',
        ],
        'udata.front': 'front = udata_front.frontend',
        'udata.apis': [
            'front_oembed = udata_front.views.oembed',
            'front_api = udata_front.api',
        ],
        'udata.harvesters': [
            'ckanpt = udata_front.harvesters.ckanpt:CkanPTBackend',
            'dadosGov = udata_front.harvesters.dadosgov:DGBackend',
            'apambiente = udata_front.harvesters.apambiente:PortalAmbienteBackend',
            'ine = udata_front.harvesters.ine:INEBackend',
            'odspt = udata_front.harvesters.odspt:OdsBackendPT',
            'dgt = udata_front.harvesters.dgt:DGTBackend',
            'dgtIne = udata_front.harvesters.dgtIne:DGTINEBackend',
        ],
        'udata.views': [
            'gouvfr_faqs = udata_front.faqs_plugin',
            'gouvfr_saml = udata_front.saml_plugin',
        ],
    },
    license='LGPL',
    zip_safe=False,
    keywords='udata opendata portal etalab',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: System :: Software Distribution",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ('License :: OSI Approved :: GNU Library or Lesser General Public '
         'License (LGPL)'),
    ],
)
