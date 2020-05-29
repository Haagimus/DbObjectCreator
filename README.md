# Database Object Creator (D.O.C.)
This library provides a method of creating database connector objects for quick and easy access to multiple
databases (both types and servers).

---

## DOC Setup
This library can be installed directly from GitHub or locally:

Run `pip install Cython` before proceeding with either install. This package is required prior to installing this library.

#### To install via GitHub
1. Run the command `pip install git+ssh://github.com/haagimus/DbObjectCreator.git`

#### To install locally
1. Clone the repo to your local machine using the Clone or Download button in the upper left
or click this download link. https://github.com/BridgeCr/DOC/archive/master.zip
2. In a terminal window navigate to the location the file was downloaded
3. Execute the following command `pip install DOC-master.zip` (change DOC-master.zip if you named it something else.)

## DOC Usage
1. Import the library into your project using `from DbObjectCreator import DbObjectCreator`
2. Create a new DbObject using `new_db = DbObjectCreator.DbObject()`
3. new_db can now be used to call multiple methods against the database.


This library supports both Windows and OSX architecture. If installing on OSX you will need FreeTDS installed.
