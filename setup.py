from setuptools import setup, find_packages
import os


version = None
with open(os.path.join(os.path.dirname(__file__), 'dumbjuice', '__version__.py')) as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"')
            break
setup(
    name="dumbjuice",
    version=version,
    packages=find_packages(include=['dumbjuice', 'dumbjuice.*']),
        package_data={
        'dumbjuice.assets': ['djicon.ico'],
    },
    include_package_data=True,  # Ensures non-Python files are included
    install_requires=[
        # Add any external dependencies your package needs here
    ],
    entry_points={
        'console_scripts': [
            'dumbjuice-build = dumbjuice.build:build',
        ],
    },
)