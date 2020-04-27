from os import getenv
from time import time

import dask.dataframe as dd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder

load_dotenv()
Session = sessionmaker(autoflush=False)


class AwsContainer:
    """
    This class outlines a generic Aws Container that can then be used to store necessary properties for use in other
    methods.
    :returns AwsContainer object
    """

    def __init__(self):
        self.tunnel = None
        self.conn_str = None
        self.engine = None
        self.local_port = None
        self.session = None

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
        try:
            # print('[SSH] Attempting to establish SSH tunnel')
            self.tunnel = SSHTunnelForwarder(
                (self.__ssh_host, self.__ssh_port),
                ssh_username=self.__ssh_user,
                ssh_pkey=self.__ssh_pk,
                remote_bind_address=(self.__db_host, self.__db_port))
            self.tunnel.daemon_forward_servers = True
            self.tunnel.start()
            self.local_port = str(self.tunnel.local_bind_port)
            # self.initialize_engine()
            # self.initialize_session()
        except BaseException as e:
            if 'Could not establish session to SSH gateway' in e.args[0]:
                print(f'{e} :: Check your VPN connection, credentials and RSA key')
            raise

    def initialize_engine(self):
        if self.local_port is None:
            self.create_tunnel()

        if self.local_port is not None:
            # print('[SQL] Generating connection string')
            self.conn_str = f"mysql+pymysql://{self.__db_user}:{self.__db_pass}@127.0.0.1:{self.local_port}/" \
                            f"{self.__db_name}"
            # print('[SQL] Creating SQL engine')
            self.engine = create_engine(self.conn_str, pool_recycle=280)

    def initialize_session(self):
        if self.engine is None:
            self.initialize_engine()

        if self.engine is not None:
            # print('[SQL] Creating SQL session')
            self.session = Session(bind=self.engine, autoflush=False, autocommit=False)

    def close_all(self):
        try:
            # print('[SQL] Disposing of SQL session')
            self.session.close()
            # print('[SQL] Disposing SQL engine')
            self.engine.dispose()
            # print('[SSH] Disposing SSH tunnel')
            self.tunnel.stop()
        except Exception as e:
            print(e)


def reflect_database_table(host, table_name=None):
    from sqlalchemy.ext.automap import automap_base

    base = automap_base()
    base.metadata.drop_all(host.engine)
    base.metadata.create_all(host.engine)

    # reflect the tables
    base.prepare(host.engine, reflect=True)
    try:
        table = base.classes[table_name]
        return table
    except KeyError:
        return 'Requested table not found'


def test_sqlalchemy_core(n=5000):
    """
    Returns a SQL query into a data frame

    Returns a DataFrame corresponding to the result set of the query
    string. Optionally provide an `index_col` parameter to use one of the
    columns as the index, otherwise default integer index will be used.

    Parameters
    ----------
    n : The number of records you want to return from the database

    Returns
    ----------
    DataFrame
    """
    # Establish the SSH connection
    host = AwsContainer()
    host.initialize_session()
    model = reflect_database_table(host=host, table_name='transaction_logs_gh')
    # t0 = time()
    # print(f'SqlAlchemy Core: Starting query for {n} items')
    t0 = time()
    temp = host.session.query(model).yield_per(200).limit(n)
    results = temp.all()
    total = time() - t0
    print(f'SqlAlchemy Core: Total time for {temp.count()} records {time() - t0}')
    host.close_all()
    return results, total


# def test_dask():
#     host = AwsContainer()
#     host.initialize_session()
#     ddf = dd.read_sql_table(table='transaction_logs_gh', uri=host.conn_str, index_col='id')
#     print(ddf)
