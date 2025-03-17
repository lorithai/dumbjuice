from setuptools import setup, find_packages

setup(
    name="dumbjuice",
    version="0.5",
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
            'dumbjuice = dumbjuice.__init__:build',
        ],
    },
)