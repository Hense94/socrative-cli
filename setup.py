from distutils.core import setup

setup(
    # Application name:
    name='socrative-cli',

    # Version number (initial):
    version='1.0.0',

    # Application author details:
    author='Henrik H. Sørensen',
    author_email='hhs19942@gmail.com',

    # Packages
    packages=['socrative-cli'],

    # Include additional files into the package
    include_package_data=True,

    # URL
    url='https://github.com/Hense94/socrative-cli',

    # License
    license='LICENSE.txt',

    # Description
    description='Answer Socrative questions through your terminal',

    long_description=open('README.md').read(),

    # Dependent packages (distributions)
    install_requires=[
        'PyInquirer',
        'click',
        'requests'
    ],
)
