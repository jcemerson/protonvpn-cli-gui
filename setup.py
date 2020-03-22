#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

from protonvpn_cli_gui.protonvpnguiapp import VERSION as pvpngui_version

# Package meta-data.
NAME = 'protonvpn-cli-gui'
DESCRIPTION = 'An unofficial GUI for ProtonVPN on Linux.'
URL = 'https://github.com/jcemerson/protonvpn-cli-gui'
LICENSE = 'GPLv3'
EMAIL = 'wutduk@pm.me'
AUTHOR = 'WutDuk'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = pvpngui_version

# Packages required to execute this module
REQUIRED = [
    'protonvpn_cli',
    'kivy',
]

# Optional packages
EXTRAS = {
    # 'fancy feature': ['django'],
}
here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))  # noqa

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    entry_points={
        "console_scripts": [
            "protonvpn-cli-gui = protonvpn_cli_gui.protonvpnguiapp:pvpn_gui"
        ]
    },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license=LICENSE,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
