from setuptools import setup

setup(
    name='wgallery',
    packages=['wgallery'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy'
    ],
)
