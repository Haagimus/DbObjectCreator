from os import getenv
from time import time

from dotenv import load_dotenv

from DBObjectCreator import DbObject, DbObjectError

load_dotenv()

# region analyticsapiprod mysql db items
# Retrieve the env variables for the ssh connection
aap_ssh_host = getenv('analytics-mysql-SSHHOST')
aap_ssh_port = int(getenv('analytics-mysql-SSHPORT'))
aap_ssh_user = getenv("analytics-mysql-SSHUSER")
aap_ssh_pk = getenv("analytics-mysql-SSHPK")

# Retrieve the env variables for the db connection
aap_db_host = getenv('analytics-mysql-HOST')
aap_db_user = getenv('analytics-mysql-USER')
aap_db_pass = getenv('analytics-mysql-PASS')
aap_db_port = int(getenv('analytics-mysql-PORT'))
aap_db_name = getenv('analytics-mysql-NAME')
# endregion
# region bridgeapiprod mysqsl db items
# Retrieve the env variables for the ssh connection
bap_ssh_host = getenv('bridge-mysql-SSHHOST')
bap_ssh_port = int(getenv('bridge-mysql-SSHPORT'))
bap_ssh_user = getenv("bridge-mysql-SSHUSER")
bap_ssh_pk = getenv("bridge-mysql-SSHPK")

# Retrieve the env variables for the db connection
bap_db_host = getenv('bridge-mysql-HOST')
bap_db_user = getenv('bridge-mysql-USER')
bap_db_pass = getenv('bridge-mysql-PASS')
bap_db_port = int(getenv('bridge-mysql-PORT'))
bap_db_name = getenv('bridge-mysql-NAME')
# endregion
# region non-prod postgresql db items
# Retrieve the env variables for the db connection
npp_db_host = getenv('np-pgsql-HOST')
npp_db_user = getenv('np-pgsql-USER')
npp_db_pass = getenv('np-pgsql-PASS')
npp_db_port = int(getenv('np-pgsql-PORT'))
npp_db_name = getenv('np-pgsql-NAME')
# endregion
# region prod postgresql db items
# Retrieve the env variables for the db connection
pp_db_host = getenv('prod-pgsql-HOST')
pp_db_user = getenv('prod-pgsql-USER')
pp_db_pass = getenv('prod-pgsql-PASS')
pp_db_port = int(getenv('prod-pgsql-PORT'))
pp_db_name = getenv('prod-pgsql-NAME')
# endregion
# region mssql db items
# Retrieve the env variables for the db connection
mss_db_host = getenv('mssql-HOST')
mss_db_port = int(getenv('mssql-PORT'))
mss_db_user = getenv('mssql-USER')
mss_db_pass = getenv('mssql-PASS')
mss_db_name = getenv('mssql-NAME')

# endregion

analyticsapiprod = DbObject(
    dbtype=1, ssh_host=aap_ssh_host, ssh_port=aap_ssh_port, ssh_pk=aap_ssh_pk, ssh_user=aap_ssh_user,
    db_host=aap_db_host, db_port=aap_db_port, db_name=aap_db_name, db_user=aap_db_user, db_pass=aap_db_pass)
bridgeapiprod = DbObject(
    dbtype=1, ssh_host=bap_ssh_host, ssh_port=bap_ssh_port, ssh_pk=bap_ssh_pk, ssh_user=bap_ssh_user,
    db_host=bap_db_host, db_port=bap_db_port, db_name=bap_db_name, db_user=bap_db_user, db_pass=bap_db_pass)
nonprodpgsql = DbObject(
    dbtype=2, db_host=npp_db_host, db_port=npp_db_port, db_name=npp_db_name, db_user=npp_db_user,
    db_pass=npp_db_pass)
prodpgsql = DbObject(
    dbtype=2, db_host=pp_db_host, db_port=pp_db_port, db_name=pp_db_name, db_user=pp_db_user,
    db_pass=pp_db_pass)
mssql = DbObject(
    dbtype=3, db_host=mss_db_host, db_port=mss_db_port, db_name=mss_db_name, db_user=mss_db_user,
    db_pass=mss_db_pass)

dbobjects = [{'db': analyticsapiprod, 'table': 'transaction_logs_gh'},
             {'db': bridgeapiprod, 'table': 'message_logs'},
             {'db': nonprodpgsql, 'table': 'oauth_access_tokens'},
             {'db': prodpgsql, 'table': 'spatial_ref_sys'},
             {'db': mssql, 'table': 'vw_ODBC_appts_Appointments'}]


def test_sqlalchemy_core():
    models = []

    try:
        for obj in dbobjects:
            t0 = time()
            print('---------------sqlalchemy operation---------------')
            print(f'Connecting to server {obj["db"].db_name}({obj["db"].db_type}).')
            obj['db'].create_tunnel()
            obj['db'].initialize_engine()

            print(f'Generating schema map for table {obj["table"]}.')
            models.append(obj['db'].reflect_database_table(obj['table']))
            total_cols = 0
            for model in models:
                total_cols += len(model.columns)
            print(f'Table consists of {total_cols} total columns')

            print(f'Time spent conducting all operations: {time() - t0:.2f} seconds.')
            obj['db'].close_all()

    except Exception as e:
        raise DbObjectError(e)


def test_specific_engine():
    for obj in dbobjects:
        t0 = time()
        if obj['db'].db_type == 'MySQL':
            print('---------------MySQL (pymysql) operations---------------')
        elif obj['db'].db_type == 'PostgreSQL':
            print('---------------PostgreSQL (psycopg2) operations---------------')
        elif obj['db'].db_type == 'MSSQL':
            print('---------------MSSQL (pymssql) operations---------------')

        print(f'Connecting to server {obj["db"].db_name}({obj["db"].db_type}).')
        obj['db'].create_tunnel()
        obj['db'].initialize_engine()

        print(f'Retrieving all rows from table {obj["table"]}.')
        results = obj['db'].string_sql_query(f'SELECT * FROM {obj["table"]}')
        print(f'Table contains {len(results)} rows.')
        print(f'Time spent retrieving data: {time() - t0: .2f} seconds.')
        obj['db'].close_all()


test_sqlalchemy_core()
test_specific_engine()
