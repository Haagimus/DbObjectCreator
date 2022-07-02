from dbobjectcreator import DbObject

dh_tables = {
    'product': '',
    'country': '', 
    'city': '', 
    'store': '', 
    'users': '', 
    'status_name': '', 
    'sale': '', 
    'order_status': ''
    }


def test_postgres_connection() -> dict:
    dh_postgres = DbObject(dbtype=2,
        db_host='localhost',
        db_port=5433, 
        db_user='datahub', 
        db_pass='c4J*wKvL3PXmmSQT', 
        db_name='datahub',
        schema='public',
    )

    dh_postgres.initialize_sa_session()
    dh_postgres.initialize_engine()

    tables_copy = dh_tables.copy()

    for table in tables_copy:
        tables_copy[table] = [col for col in dh_postgres.reflect_database_table(table).columns]
    
    return tables_copy

def test_mysql_connection() -> dict:
    dh_mysql = DbObject(dbtype=1,
        db_host='localhost',
        db_port=3307,
        db_user='root',
        db_pass='c4J*wKvL3PXmmSQT',
        db_name='datahub',
    )

    dh_mysql.initialize_sa_session()
    dh_mysql.initialize_engine()

    for table in dh_tables:
        dh_tables[table] = [col for col in dh_mysql.reflect_database_table(table).columns]

    return dh_tables

for table, columns in test_postgres_connection().items():
    print(table, [columns[i].name for i in range(len(columns))], sep='\n', end='\n\n')


for table, columns in test_mysql_connection().items():
    print(table, [columns[i].name for i in range(len(columns))], sep='\n', end='\n\n')