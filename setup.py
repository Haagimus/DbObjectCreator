from setuptools import setup, find_packages

setup(
    name='DbObjectCreator',
    version=open('version.txt').read(),
    author="haagimus",
    author_email="ghaag@bridgeconnector.com",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=open('requirements.txt').read()
)