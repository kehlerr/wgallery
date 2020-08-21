from setuptools import setup

setup(
    name='wwwgallery',
    packages=['gallery'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
