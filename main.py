from os import getenv
from time import time

from dotenv import load_dotenv

import DBObjectCreator

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


def test_sqlalchemy_core():
    # Establish the SSH connection
    t0 = time()
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

    dbobjects = [analyticsapiprod, bridgeapiprod, nonprodpgsql, prodpgsql, mssql]
    # dbobjects = [mssql]

    try:
        for obj in dbobjects:
            obj.create_tunnel()
            obj.initialize_engine()
        obj = None

        aapmodel = analyticsapiprod.reflect_database_table(table_name='transaction_logs_gh')
        bapmodel = bridgeapiprod.reflect_database_table(table_name='message_logs')
        nppmodel = nonprodpgsql.reflect_database_table(table_name='users')
        ppmodel = prodpgsql.reflect_database_table(table_name='connectors')
        mssqlmodel = mssql.reflect_database_table(table_name='spt_monitor')
    except Exception as e:
        for obj in dbobjects:
            obj.close_all()
        raise e
        return

    total_cols = len(aapmodel.columns) + len(bapmodel.columns) + len(nppmodel.columns) + len(ppmodel.columns) + len(
        mssqlmodel.columns)
    # total_cols = len(mssqlmodel.columns)
    print(
        f'Total time connecting to {len(dbobjects)} database servers and generating schema map on {total_cols} '
        f'columns: {time() - t0:.2f} seconds')
    for obj in dbobjects:
        obj.close_all()


test_sqlalchemy_core()

