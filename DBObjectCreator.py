from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder
import mysql.connector

load_dotenv()
Session = sessionmaker(autoflush=False)


class DbObject:
    """
    This class outlines a generic DB object that can then be used to store necessary properties for use in other
    methods.

    :return: a db object with the necessary
    :type: class object
    """

    def __init__(self, dbtype=None, ):
        self.tunnel = None
        self.engine = None
        self.session = None
        self.cursor = None
        self.__conn_str = None
        self.__local_port = None
        self.__local_address = None

        self.__db_type = dbtype

        # Retrieve the env variables for the ssh connection
        self.__ssh_host = getenv('SSHHOST')
        self.__ssh_port = int(getenv('SSHPORT'))
        self.__ssh_user = getenv("SSHUSER")
        self.__ssh_pk = "assets/ssh_pk.pem"

        # Retrieve the env variables for the db connection
        self.__db_host = getenv('DBHOST')
        self.__db_port = int(getenv('DBPORT'))
        self.__db_user = getenv('DBUSER')
        self.__db_name = getenv('DBNAME')
        self.__db_pass = getenv('DBPASS')

    def create_tunnel(self):
        """Creates an SSH tunnel to allow connecting to an AWS service.
        Nothing is returned but the self.tunnel property is set.
        """
        try:
            # print('[SSH] Attempting to establish SSH tunnel')
            self.tunnel = SSHTunnelForwarder(
                (self.__ssh_host, self.__ssh_port),
                ssh_username=self.__ssh_user,
                ssh_pkey=self.__ssh_pk,
                remote_bind_address=(self.__db_host, self.__db_port))
            self.tunnel.daemon_forward_servers = True
            self.tunnel.start()
            self.__local_port = str(self.tunnel.local_bind_port)
            self.__local_address = str(self.tunnel.local_bind_address)
        except BaseException as e:
            if 'Could not establish session to SSH gateway' in e.args[0]:
                print(f'CRITICAL :: {e} :: Check your VPN connection, credentials and RSA key')
            raise

    def initialize_engine(self):
        """Creates a sqlalchemy engine.
        Nothing is returned but the self.conn_str and
        self.engine properties are set.
        """
        if self.__local_port is None:
            self.create_tunnel()

        if self.__local_port is not None:
            # print('[SQL] Generating connection string')
            self.__conn_str = f"mysql+pymysql://{self.__db_user}:{self.__db_pass}@127.0.0.1:{self.__local_port}/" \
                            f"{self.__db_name}"
            # print('[SQL] Creating SQL engine')
            self.engine = create_engine(self.__conn_str, pool_recycle=280)

    def initialize_session(self):
        """Creates a sessionmaker factory that can be used to run queries against the database.
        Nothing is returned but the self.session property is set.
        """
        if self.engine is None:
            self.initialize_engine()

        if self.engine is not None:
            # print('[SQL] Creating SQL session')
            self.session = Session(bind=self.engine, autoflush=False, autocommit=False)

    def create_cursor(self):
        """Create a new cursor to execute queries with.

        :return: a cursor that can be used to execute queries
        :rtype: cursor
        """
        with self.tunnel:
            cnx = mysql.connector.connect(host=self.__local_address,
                                          port=self.__local_port,
                                          user=self.__db_user,
                                          password=self.__db_pass,
                                          database=self.__db_name)
        self.cursor = cnx.cursor()

    def close_all(self):
        """Closes any existing database connections/sessions/cursors if they are open.

        :return: None
        :rtype: None
        """
        try:
            if self.cursor is not None:
                self.cursor.close()
            # print('[SQL] Disposing of SQL session')
            if self.session is not None:
                self.session.close()
            # print('[SQL] Disposing SQL engine')
            if self.engine is not None:
                self.engine.dispose()
            # print('[SSH] Disposing SSH tunnel')
            if self.tunnel is not None:
                self.tunnel.stop()
        except Exception as e:
            print(e)

    def reflect_database_table(self, table_name=None):
        """Generates an ORM model of the passed in table and returns the object and also a
        separate list containing just the column headers
        :param table_name: the table name you want to generate a class mode for
        :type table_name: str
        :return: requested table generated base class | list of table column headers
        :rtype: DeclarativeMeta | List
        """
        from sqlalchemy.ext.automap import automap_base

        base = automap_base()
        base.metadata.drop_all(self.engine)
        base.metadata.create_all(self.engine)

        # reflect the tables
        base.prepare(self.engine, reflect=True)
        try:
            table = base.classes[table_name]
            cols = [attr for attr in dir(table) if not attr.startswith('_')]
            return table, cols
        except KeyError:
            return 'Requested table not found'
