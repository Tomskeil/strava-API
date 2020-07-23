from setuptools import setup, find_packages

setup(
    name='StravaAPI',
    version='0.0.1',
    packages=find_packages(),
    license='MIT',
    description='Python Strava API Wrapper',
    long_description=open('README.md').read(),
    install_requires=['requests'],
    author='Thomas Keil',
    author_email='tomskeil@hotmail.com'
)
