# Database Object Creator (D.O.C.)
This library provides a method of creating database connector objects for quick and easy access to multiple
databases (both types and servers).

---

## DOC Setup
Clone to your project directory and run `python setup.py bdist_wheel` to install.

## DOC Usage
1. Import the library into your project using `from DbObjectCreator import DbObject, DbObjectError`
2. Create a new DbObject using `new_db = DbObject()`
3. new_db can now be used to call multiple methods against the database.


This library supports both Windows and OSX architecture. If installing on OSX you will need FreeTDS installed.
