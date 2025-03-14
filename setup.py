from setuptools import setup, find_packages

setup(
    name="dumbjuice",
    version="0.1",
    packages=find_packages(),
        package_data={
        'dumbjuice.assets': ['icon.ico'],
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