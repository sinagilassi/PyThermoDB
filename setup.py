from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

APP_NAME = 'PyThermoDB'
VERSION = '1.11.12'
AUTHOR = 'Sina Gilassi'
EMAIL = '<sina.gilassi@gmail.com>'
DESCRIPTION = (
    'PyThermoDB is a lightweight and user-friendly Python package designed to '
    'provide quick access to essential thermodynamic data.'
)
LONG_DESCRIPTION = "The Python Thermodynamics Databook (PyThermoDB) is a lightweight and user-friendly Python package designed to provide quick access to essential thermodynamic data. Whether you're a student, researcher, or engineer, this package serves as a valuable resource for retrieving thermodynamic properties, equations, and constants."
HOME_PAGE = 'https://github.com/sinagilassi/PyThermoDB'
DOCUMENTATION = 'https://pythermodb.readthedocs.io/en/latest/'

# Setting up
setup(
    name=APP_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    url=HOME_PAGE,
    project_urls={
        'Documentation': DOCUMENTATION,
        'Source': HOME_PAGE,
        'Tracker': f'{HOME_PAGE}/issues',
    },
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    include_package_data=True,  # Make sure to include non-Python files
    # Add both config and data files
    package_data={
        'pyThermoDB': [
            'config/*.yml',
            'data/*.csv',
            'templates/*.html',
            'static/*',
            'static/**/*'  # Include subdirectories
        ]
    },
    # Add license file
    license='MIT',
    license_files=[],
    install_requires=[
        'pandas',
        'requests',
        'numpy',
        'PyYAML'
    ],
    extras_require={
        'web': ['jinja2'],
    },
    keywords=[
        'chemical engineering',
        'thermodynamics',
        'thermodynamic data'
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.13",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.10',
)
