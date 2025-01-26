from setuptools import setup, find_packages

setup(
    name='verdictnet',
    version='0.0.1',
    description='A tool to do verdictnet queries on large documents',
    author='Alex Monras',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'}
)
