#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='django-passkeys',
    version='0.4.0',
    description='A Django Authentication Backend for Passkeys',
    #long_description=open("README.md").read(),
    #long_description_content_type="text/markdown",
    long_description = "Use Passkeys in Django",

    author='Mohamed El-Kalioby',
    author_email = 'mkalioby@mkalioby.com',
    url = 'https://github.com/mkalioby/django-passkeys',
    download_url='https://github.com/mkalioby/django-passkeys',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'django >= 2.0',
        'ua-parser',
        'user-agents',
        'fido2 == 1.1.0',
      ],
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False, # because we're including static files
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
]
)
