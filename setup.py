from setuptools import setup
import fixfuture

setup(
    name='fix-future',
    version=fixfuture.__version__,
    packages=['fixfuture'],
    url='',
    license='',
    author='Luc PHAN',
    author_email='',
    description='',
    entry_points={'console_scripts': ['fix-future = fixfuture.command:main']},
    install_requires=['clize', 'prettytable'],
    include_package_data=True
)
