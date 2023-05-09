#!/usr/bin/env python

import os

from setuptools import setup, find_packages


def file_content(filename):
    '''Load file content'''
    with open(filename) as ifile:
        return ifile.read()


def get_requirements():
    '''Return content of pip requirements file with very custom logic'''
    reqs = file_content(os.path.join('requirements', 'udata.pip')).splitlines()
    # keep only the ref to udata, unpinned if not udata==xxx
    reqs = [r for r in reqs if r.strip().startswith('udata==')] or ['udata']
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
    url='https://dados.gov.pt/',
    author='AMA - Agência para a Modernização Administrativa',
    author_email='ama@ama.pt',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=get_requirements(),
    entry_points={
        'udata.themes': [
            'gouvpt = udata_front.theme.gouvpt',
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
            'maaf = udata_front.harvesters.maaf:MaafBackend',
            'ckanpt = udata_front.harvesters.ckanpt:CkanPTBackend',
            'dadosGov = udata_front.harvesters.dadosgov:DGBackend',
            'apambiente = udata_front.harvesters.apambiente:PortalAmbienteBackend',
            'ine = udata_front.harvesters.ine:INEBackend',
            'odspt = udata_front.harvesters.odspt:OdsBackendPT',
            'dgt = udata_front.harvesters.dgt:DGTBackend'
        ],
        'udata.views': [
            'gouvpt_faqs = udata_front.faqs_plugin',
            #'gouvpt_saml = gouvpt.saml_plugin',
        ],
        'udata.tasks': [
            'front = udata_front.tasks',
        ],
    },
    license='AGPL',
    zip_safe=False,
    keywords='udata theme gouvpt portugal',
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
