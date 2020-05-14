from setuptools import setup, find_packages
import DbObjectCreator.__init__ as init

with open('README.md', 'r') as ld:
    long_description = ld.read()

setup(
    name='DbObjectCreator',
    version=init.__version__,
    author=init.__author__,
    author_email="haagimus@gmail.com",
    description='A database object creator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/haagimus/DbObjectCreator.git',
    packages=['DbObjectCreator'],
    install_requires=open('requirements.txt').read(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.7'
)
