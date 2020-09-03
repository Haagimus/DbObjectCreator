# Database Object Creator (D.O.C.)
This library provides a method of creating database connector objects for quick and easy access to multiple
databases (both types and servers).

---

## DOC Setup
This library can be installed via Pypi.org[https://pypi.org/project/DbObjectCreator/] or locally:

Run `pip install Cython` before proceeding with either install. This package is required prior to installing this library.
This library can now be installed by running `pip install DbObjectCreator`

## DOC Usage
1. Import the library into your project using `from DbObjectCreator import DbObjectCreator`
2. Create a new DbObject using `new_db = DbObjectCreator.DbObject()`
3. new_db can now be used to call multiple methods against the database.


This library supports both Windows and OSX architecture. If installing on OSX you will need FreeTDS installed.
