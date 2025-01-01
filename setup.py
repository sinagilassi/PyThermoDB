from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

APP_NAME = 'PyThermoDB'
VERSION = '1.7.10'
AUTHOR = 'Sina Gilassi'
EMAIL = '<sina.gilassi@gmail.com>'
DESCRIPTION = 'PyThermoDB is a lightweight and user-friendly Python package designed to provide quick access to essential thermodynamic data.'
LONG_DESCRIPTION = "The Python Thermodynamics Databook (PyThermoDB) is a lightweight and user-friendly Python package designed to provide quick access to essential thermodynamic data. Whether you're a student, researcher, or engineer, this package serves as a valuable resource for retrieving thermodynamic properties, equations, and constants."

# Setting up
setup(
    name=APP_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    include_package_data=True,  # Make sure to include non-Python files
    # Add both config and data files
    package_data={'': ['config/*.yml', 'data/*.csv']},
    license='MIT',
    install_requires=['pandas', 'pillow', 'requests',
                      'urllib3', 'numpy', 'PyYAML', 'sympy', 'flask'],
    keywords=['python', 'chemical engineering', 'thermodynamics',
              'PyThermoDB', 'thermodynamic data'],
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
