import mysql.connector
from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql.elements import BinaryExpression
from sshtunnel import SSHTunnelForwarder
import pymysql
import psycopg2
import pymssql
import os

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

    def __init__(self, dbtype, db_host, db_port, db_user, db_pass, db_name=None,
                 ssh_host=None, ssh_port=None, ssh_pk=None, ssh_user=None, tunnel=None, sa_engine=None,
                 engine=None, sa_session=None, session=None, cursor=None, conn_str=None, local_port=None,
                 local_addr=None, schema=None):
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
        sa_session: sessionmaker
            Manages persistence operations for ORM-mapped objects.
        session: sessionmaker
            Manages persistence operations for raw sql queries.
        cursor: object
            This is the object you use to interact with the database.
        conn_str: str
            The constructed connection string for the host database server.
        local_port: int
            The local port provided by the tunnel local_bind_port
        local_addr: str
            The local address provided by the tunnel local_bind_address.
        schema: str
            (Only applies to PostgreSQL and MSSQL) The schema name that you want to manipulate tables and data within.
        """
        self.db_type: int = DbType(dbtype).name
        self.ssh_host: str = ssh_host
        self.ssh_port: int = ssh_port
        self.ssh_pk: str = ssh_pk
        self.ssh_user: str = ssh_user
        self.db_host: str = db_host
        self.db_port: int = db_port
        self.db_name: str = db_name
        self.db_user: str = db_user
        self.db_pass: str = db_pass
        self.tunnel: SSHTunnelForwarder = tunnel
        self.sa_engine: object = sa_engine
        self.engine: object = engine
        self.sa_session: sessionmaker = sa_session
        self.session: sessionmaker = session
        self.cursor: object = cursor
        self.conn_str: str = conn_str
        self.local_port: int = local_port
        self.local_address: str = local_addr
        self.schema: str = schema

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
            try:
                if self.tunnel and self.local_port is not None:
                    # If there is an SSH tunnel try and connect through the local host and port
                    self.engine = pymysql.connect(user=self.db_user, passwd=self.db_pass,
                                                  host='127.0.0.1', port=self.local_port,
                                                  database=self.db_name)
                else:
                    # if there is no SSH tunnel try and connect directly to the host and port
                    self.engine = pymysql.connect(user=self.db_user, passwd=self.db_pass,
                                                  host=self.db_host, port=self.db_port,
                                                  database=self.db_name)
            except Exception as e:
                raise DbObjectError(e)
        elif self.db_type == 'PostgreSQL':
            try:
                self.engine = psycopg2.connect(user=self.db_user, password=self.db_pass,
                                               host=self.db_host, port=self.db_port,
                                               database=self.db_name)
            except Exception as e:
                raise DbObjectError(e)
        elif self.db_type == 'MSSQL':
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
            if self.tunnel is not None:
                self.conn_str = f"mysql+pymysql://{self.db_user}:{self.db_pass}@" \
                                f"localhost:{self.local_port}/{self.db_name}"
            elif self.tunnel is None:
                self.conn_str = f"mysql+pymysql://{self.db_user}:{self.db_pass}@" \
                                f"{self.db_host}:{self.db_port}/{self.db_name}"
            else:
                raise DbObjectError(
                        'SSH tunnel not established, please setup the SSH tunnel before attempting to connect the engine.')
        elif self.db_type == 'PostgreSQL':
            self.conn_str = f"postgresql+psycopg2://{self.db_user}:{self.db_pass}@" \
                            f"{self.db_host}:{self.db_port}/{self.db_name}"
        elif self.db_type == 'MSSQL':
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
            self.session = Session(bind=self.engine, autoflush=False, autocommit=False)

    def initialize_sa_session(self):
        """Creates a sessionmaker factory that can be used to run queries against the database and also sets the self.session property.

        Yields
        ----------
        self.session : Session
            A sessionmaker session for executing queries
        """
        if not hasattr(self, 'sa_engine'):
            self.initialize_engine()

        elif hasattr(self, 'sa_engine'):
            self.sa_session = Session(bind=self.sa_engine, autoflush=False, autocommit=False)

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

        if hasattr(self, 'sa_engine'):
            base = automap_base()
            base.metadata.drop_all(self.sa_engine)
            base.metadata.create_all(self.sa_engine)

            # reflect the tables
            if self.db_type == 'PostgreSQL':
                base.prepare(self.sa_engine, reflect=True, schema=self.schema)
            else:
                base.prepare(self.sa_engine, reflect=True)
            try:
                if self.db_type == 'PostgreSQL':
                    table = base.metadata.tables[self.schema + '.' + table_name]
                else:
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
                    cnx = mysql.connector.connect(
                            host=self.local_address,
                            port=self.local_port,
                            user=self.db_user,
                            password=self.db_pass,
                            database=self.db_name)
            elif self.db_type == 'PostgreSQL':
                cnx = psycopg2.connect(
                        host=self.db_host,
                        port=self.db_port,
                        user=self.db_user,
                        password=self.db_pass,
                        database=self.db_name)
            elif self.db_type == 'MSSQL':
                cnx = pymssql.connect(
                        host=self.db_host,
                        port=self.db_port,
                        user=self.db_user,
                        password=self.db_pass,
                        database=self.db_name)
        except Exception as e:
            raise DbObjectError(e)
        self.cursor = cnx.cursor()

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

    def orm_get_rows(self, table_name, filter_text=None, distinct=False, delete=False):
        """
        Returns all rows from selected columns in a table, provides options to filter your query and return only
        distinct values.

        Parameters
        ----------
        table_name: str | DeclarativeMeta
            The table name you want to search within. Alternatively an ORM model may be passed directly.
        filter_text: str | dict
            Text that you want to filter source by. Allows a dict of multiple filter texts to be passed.
        distinct: bool
            True indicates you only want distinct source without duplicates.
        delete : bool
            True indicates you want to delete all returned rows from the target table.

        Returns
        ----------
        source : list
        """
        self.session = Session(bind=self.sa_engine)
        if type(table_name) == str:
            table_model = self.reflect_database_table(table_name=table_name)
        else:
            table_model = table_name
        if filter_text is None:
            if distinct:
                results = Query(table_model, self.session).distinct().all()
            else:
                results = Query(table_model, self.session).all()
        elif type(filter_text) == dict:
            query = Query(table_model, self.session)
            for attr, value in filter_text.items():
                if value == '':
                    pass
                else:
                    query = Query(table_model, self.session).filter(getattr(table_model, attr) == value, )
            if distinct:
                results = query.distinct().all()
            else:
                results = query.all()
        elif type(filter_text) == BinaryExpression:
            if distinct:
                results = Query(table_model, self.session).filter(filter_text).distinct().all()
            else:
                results = Query(table_model, self.session).filter(filter_text).all()
        else:
            if distinct:
                results = Query(table_model, self.session).filter(filter_text).distinct().all()
            else:
                results = Query(table_model, self.session).filter(filter_text).all()

        if delete and len(results) > 0:
            print(f'Attempting to delete {len(results)} from {table_name.name}.')
            try:
                if filter_text is None:
                    Query(table_model, self.session).delete(synchronize_session=False)
                else:
                    Query(table_model, self.session).filter(filter_text).delete(synchronize_session=False)
                self.session.commit()
                return
            except Exception as e:
                print(f'ERROR:: The delete operation was unsuccessful, operation aborted.')
                self.session.rollback()
                raise DbObjectError(e)

        return results


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
