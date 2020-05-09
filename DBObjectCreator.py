import mysql.connector
from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder
import pandas as pd

Session = sessionmaker(autoflush=False)


class DbType(Enum):
    MySQL = 1
    PostgreSQL = 2
    MSSQL = 3


class DbObject:
    """
    This class outlines a generic DB object that can then be used to store necessary properties for use in other methods.

    Yields
    ----------
    DbObject
        A DbObject class object
    """

    def __init__(self, dbtype, db_host, db_port, db_name, db_user, db_pass,
                 ssh_host=None, ssh_port=None, ssh_pk=None, ssh_user=None, tunnel=None, sa_engine=None,
                 engine=None, session=None, cursor=None, conn_str=None, local_port=None, local_addr=None):
        """Create a new :class:`.DbObject` instance.

        Summary
        ----------
        This will create a DbObject which contains all necessary properties and methods to interact with a database.

        Parameters
        ----------
        dbtype: int
            This is the database type for this object, used to generate the correct connection string.
            1 = MySQL | 2 = PostgreSQL | 3 = MSSQL
        ssh_host : str
            This is the host address of the SSH tunnel.
        ssh_port : int
            This is the port of the SSH tunnel.
        ssh_pk : file
            This is the file path to the RSA private key pem file.
        ssh_user : str
            This is the SSH login username.
        db_host : str
            This is the database host address.
        db_port : int
            This is the database host port.
        db_name : str
            This is the database name for the host server.
        db_user : str
            This is the login account name for the database.
        db_pass : str
            This is the login account password for the database.
        tunnel: SSHTunnelForwarder
            This is an established SSH Tunnel proxy when established.
        sa_engine: object
            This is a sqlalchemy database connection engine used for performing reflections and orm queries.
        engine: object
            This is a database specific connection engine used for raw sql query execution.
        session: sessionmaker
            Manages persistence operations for ORM-mapped objects.
        cursor: object
            This is the object you use to interact with the database.
        conn_str: str
            The constructed connection string for the host database server.
        local_port: int
            The local port provided by the tunnel local_bind_port
        local_addr: str
            The local address provided by the tunnel local_bind_address.
        """
        self._db_type: int = DbType(dbtype).name
        self.__ssh_host: str = ssh_host
        self.__ssh_port: int = ssh_port
        self.__ssh_pk: str = ssh_pk
        self.__ssh_user: str = ssh_user
        self.__db_host: str = db_host
        self.__db_port: int = db_port
        self.__db_name: str = db_name
        self.__db_user: str = db_user
        self.__db_pass: str = db_pass
        self._tunnel: SSHTunnelForwarder = tunnel
        self._sa_engine: object = sa_engine
        self._engine: object = engine
        self._session: sessionmaker = session
        self._cursor: object = cursor
        self._conn_str: str = conn_str
        self._local_port: int = local_port
        self._local_address: str = local_addr

    # region Getters and Setters for the object
    @property
    def db_type(self):
        return self._db_type

    @db_type.setter
    def db_type(self, db_type):
        self._db_type = DbType(db_type).name

    @property
    def ssh_host(self):
        return self.__ssh_host

    @ssh_host.setter
    def ssh_host(self, ssh_host):
        self.__ssh_host = ssh_host

    @property
    def ssh_port(self):
        return self.__ssh_port

    @ssh_port.setter
    def ssh_port(self, ssh_port):
        self.__ssh_port = ssh_port

    @property
    def ssh_pk(self):
        return self.__ssh_pk

    @ssh_pk.setter
    def ssh_pk(self, ssh_pk):
        self.__ssh_pk = ssh_pk

    @property
    def ssh_user(self):
        return self.__ssh_user

    @ssh_user.setter
    def ssh_user(self, ssh_user):
        self.__ssh_user = ssh_user

    @property
    def db_host(self):
        return self.__db_host

    @db_host.setter
    def db_host(self, db_host):
        self.__db_host = db_host

    @property
    def db_port(self):
        return self.__db_port

    @db_port.setter
    def db_port(self, db_port):
        self.__db_port = db_port

    @property
    def db_name(self):
        return self.__db_name

    @db_name.setter
    def db_name(self, db_name):
        self.__db_name = db_name

    @property
    def db_user(self):
        return self.__db_user

    @db_user.setter
    def db_user(self, db_user):
        self.__db_user = db_user

    @property
    def db_pass(self):
        return self.__db_pass

    @db_pass.setter
    def db_pass(self, db_pass):
        self.__db_pass = db_pass

    @property
    def tunnel(self):
        return self._tunnel

    @tunnel.setter
    def tunnel(self, tunnel):
        self._tunnel = tunnel

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, engine):
        self._engine = engine

    @property
    def sa_engine(self):
        return self._sa_engine

    @sa_engine.setter
    def sa_engine(self, sa_engine):
        self._sa_engine = sa_engine

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        self._session = session

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, cursor):
        self._cursor = cursor

    @property
    def conn_str(self):
        return self._conn_str

    @conn_str.setter
    def conn_str(self, conn_str):
        self._conn_str = conn_str

    @property
    def local_port(self):
        return self._local_port

    @local_port.setter
    def local_port(self, local_port):
        self._local_port = local_port

    @property
    def local_address(self):
        return self._local_address

    @local_address.setter
    def local_address(self, local_address):
        self._local_address = local_address

    # endregion

    def create_tunnel(self):
        """Creates an SSH proxy tunnel for secure connections then binds that tunnel to the _tunnel property of the DbObject.

        Parameters
        ----------

        Yields
        ----------
        self._tunnel : SSHTunnelForwarder
            A secure proxy tunnel connection
        """
        if self.db_type == 'MySQL':
            try:
                self.tunnel = SSHTunnelForwarder(
                    (self.ssh_host, self.ssh_port),
                    ssh_username=self.ssh_user,
                    ssh_pkey=self.ssh_pk,
                    remote_bind_address=(self.db_host, self.db_port))
                self.tunnel.daemon_forward_servers = True
                self.tunnel.start()
                self.local_port = int(self.tunnel.local_bind_port)
                self.local_address = str(self.tunnel.local_bind_address)
            except Exception as e:
                raise DbObjectError(f'{e} for {self.db_name}({self.db_type})')
        elif self.db_type == 'PostgreSQL' or self._db_type == 'MSSQL':
            # The database is either a postgresql or mssql which do not require an SSH Tunnel proxy so just pass
            pass

    def initialize_engine(self):
        """Instantiates a sqlalchemy engine for the requested database then binds the connection string and engine to their respective properties within the DbObject.

        Yields
        ----------
        self.engine : object
            A created sqlalchemy database engine
        """

        # Create a sqlalchemy engine for the DbObject
        self.connection_string_builder()
        self.sa_engine = create_engine(self.conn_str)

        # Create a database type specific engine for the DbObject
        if self.db_type == 'MySQL':
            import pymysql
            try:
                self.engine = pymysql.connect(user=self.db_user, passwd=self.db_pass,
                                              host='127.0.0.1', port=self.local_port,
                                              database=self.db_name)
            except Exception as e:
                raise DbObjectError(e)
        elif self.db_type == 'PostgreSQL':
            import psycopg2
            try:
                self.engine = psycopg2.connect(user=self.db_user, password=self.db_pass,
                                               host=self.db_host, port=self.db_port,
                                               database=self.db_name)
            except Exception as e:
                raise DbObjectError(e)
        elif self.db_type == 'MSSQL':
            import pymssql
            try:
                self.engine = pymssql.connect(user=self.db_user, password=self.db_pass,
                                              host=f'{self.db_host}:{self.db_port}',
                                              database=self.db_name)
            except Exception as e:
                raise DbObjectError(e)

    def connection_string_builder(self):
        """This just builds a database server connection string based on the self.db_type property.

        Yields
        ----------
        self.conn_str : str
            A generated database connection string.
        """
        if self.db_type == 'MySQL':
            if hasattr(self, '_tunnel'):
                self.conn_str = f"mysql+pymysql://{self.db_user}:{self.db_pass}@" \
                                f"localhost:{self.local_port}/{self.db_name}"
            else:
                raise DbObjectError(
                    'SSH tunnel not established, please setup the SSH tunnel before attempting to connect the engine.')
        elif self.db_type == 'PostgreSQL':
            self.conn_str = f"postgresql+psycopg2://{self.db_user}:{self.db_pass}@" \
                            f"{self.db_host}:{self.db_port}/{self.db_name}"
        elif self.db_type == 'MSSQL':
            import os

            if os.name == 'nt':
                self.conn_str = f'mssql://{self.db_user}:{self.db_pass}@' \
                                f'{self.db_host}:{self.db_port}/{self.db_name}?driver=SQL+Server'
            elif os.name == 'posix':
                self.conn_str = f'mssql+pyodbc://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/' \
                                f'{self.db_name}?driver=FreeTDS'
        else:  # The db type is not defined
            raise DbObjectError('Database Type (dbtype) not defined, please define the database type using '
                                'object.db_type before attempting to establish the SSH Tunnel.')

    def initialize_session(self):
        """Creates a sessionmaker factory that can be used to run queries against the database and also sets the self.session property.

        Yields
        ----------
        self.session : Session
            A sessionmaker session for executing queries
        """
        if not hasattr(self, 'engine'):
            self.initialize_engine()

        elif hasattr(self, 'engine'):
            self._session = Session(bind=self._engine, autoflush=False, autocommit=False)

    def reflect_database_table(self, table_name=None):
        """Generates a class model of the requested table.

        Parameters
        ----------
        table_name : str
            The table name you want to generate a class mode for.

        Returns
        ----------
        table : class
            Requested table generated base class.
        """
        from sqlalchemy.ext.automap import automap_base

        if hasattr(self, 'engine'):
            base = automap_base()
            base.metadata.drop_all(self.sa_engine)
            base.metadata.create_all(self.sa_engine)

            # reflect the tables
            base.prepare(self.sa_engine, reflect=True)
            try:
                table = base.metadata.tables[table_name]
                return table
            except BaseException as e:
                raise DbObjectError(e)
        else:
            raise DbObjectError('No engine has been initialized for this object, please execute obj.initialize_engine()'
                                ' and try the reflection again.')

    def create_cursor(self):
        """Create a new cursor to execute queries with.

        Returns
        ----------
        cursor : cursor
             A cursor that can be used to execute queries
        """
        try:
            if self.db_type == 'MySQL':
                with self.tunnel:
                    cnx = mysql.connector.connect(host=self.local_address,
                                                  port=self.local_port,
                                                  user=self.db_user,
                                                  password=self.db_pass,
                                                  database=self.db_name)
            elif self.db_type == 'PostgreSQL' or self.db_type == 'MSSQL':
                cnx = mysql.connector.connect(host=self.db_host,
                                              port=self.db_port,
                                              user=self.db_user,
                                              password=self.db_pass,
                                              database=self.db_name)
        except Exception as e:
            raise DbObjectError(e)
        self._cursor = cnx.cursor()

    def close_all(self):
        """Closes any existing database workers if they are open. Includes cursors, sessions, engines and tunnels.

        Returns
        ----------
        None
        """
        try:
            if self.engine is not None:
                self.engine.close()
            if self.sa_engine is not None:
                self.sa_engine.dispose()
            if self.tunnel is not None:
                self.tunnel.stop()
        except Exception as e:
            raise DbObjectError(e)

    def orm_sql_query(self):
        try:
            self.initialize_session()
            # TODO: Write this function
        finally:
            self.session.close()

    def string_sql_query(self, query=None):
        """Attempts to execute the passed in query argument.

        Parameters
        ----------
        query : str
            The raw sql query that you want to execute.

        Returns
        ----------
        dict : tuple
            Dictionary of tuples containing the requested table rows.
        """

        try:
            with self.engine.cursor() as cursor:
                cursor.execute(query)
                rs = cursor.fetchall()
            return rs

        except Exception as e:
            raise DbObjectError(e)


class DbObjectError(Exception):
    """A custom exception handler for internal errors."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'DbObjectError, {self.message}'
        else:
            return 'DbObjectError has been raised'