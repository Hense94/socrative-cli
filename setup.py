from distutils.core import setup

setup(
    # Application name:
    name='socrativecli',

    # Version number (initial):
    version='1.0.0',

    # Application author details:
    author='Henrik H. Sørensen',
    author_email='hhs19942@gmail.com',

    # Packages
    packages=['socrativecli'],

    # Include additional files into the package
    include_package_data=True,

    # URL
    url='https://github.com/Hense94/socrativecli',

    # License
    license='LICENSE.txt',

    # Description
    description='Answer Socrative questions through your terminal',

    long_description=open('README').read(),

    # Dependent packages (distributions)
    install_requires=[
        'PyInquirer',
        'click',
        'requests'
    ],

    entry_points={
        'console_scripts': ['socrative-cli=socrativecli.main:main']
    }
)
