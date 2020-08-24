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
		url='https://github.com/Haagimus/DbObjectCreator/releases/tag/v1.0.12',
		packages=['DbObjectCreator'],
		install_requires=[
			'bcrypt',
			'cffi',
			'cryptography',
			'Cython',
			'mysql',
			'mysql-connector',
			'mysqlclient',
			'numpy',
			'pandas',
			'paramiko',
			'psycopg2',
			'pycparser',
			'pymssql',
			'PyMySQL',
			'PyNaCl',
			'python-dateutil',
			'pytz',
			'six',
			'SQLAlchemy',
			'sshtunnel',
			'wheel'
		],
		classifiers=[
			'Programming Language :: Python :: 3',
			'License :: OSI Approved :: MIT License',
			'Operating System :: OS Independent'
		],
		python_requires='>=3.7'
)
