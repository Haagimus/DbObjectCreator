from time import time

from DBObjectCreator import DbObject


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
    host = DbObject()
    host.initialize_session()
    model = host.reflect_database_table(table_name='transaction_logs_gh')
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
