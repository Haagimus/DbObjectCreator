from setuptools import setup, find_packages

with open('README.md', 'r') as ld:
    long_description = ld.read()

setup(
    name='DbObjectCreator',
    version='0.9',
    author="Haagimus",
    author_email="ghaag@bridgeconnector.com",
    description='A database object creator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/BridgeCr/DOC.git',
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=open('requirements.txt').read(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
