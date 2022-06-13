from pydoc import classname

from dbobjectcreator.DbObjectCreator import DbObject
from pandas import DataFrame
from sqlalchemy import inspect

from console_progress import progress_bar
from pipeline_wrapper import commit_session
from variable_loader import is_local


class RowFactory(object):
    """
    A Factory that creates a dynamically created add and remove function for a database target table.
    """
    @staticmethod
    def add_rows(new_data: DataFrame, table_model: classname, dbo: DbObject):
        f"""
        Add a DataFrame of rows to the {table_model} database table.

        Parameters
        ----------
        new_data : DataFrame
            A DataFrame containing the entries you want to have added to the {table_model} database table.
        table_model : object
            The object model you want to target while adding {new_data} from the {table_model} database table.
        dbo : DbObject
            Allows access to all methods and properties of the desired {dbo} DbObject.
      """
        for c1 in table_model.__table__.columns:
            if str(c1).split('.')[1] in new_data.columns.values:
                # Table and new_data models' match let's continue
                continue
            else:
                # Table and new_data models' do not match let's stop
                return 'ERROR'

        print(f'Inserting {table_model.__tablename__} rows that do not exist in the existing database...')
        for row in new_data if not is_local else progress_bar(new_data):
            entry = table_model()
            table_cols = inspect(table_model).columns
            [setattr(entry, col.name, getattr(row, col.name)) for col in table_cols]
            dbo.sa_session.add(entry)
        commit_session(dbo)

    @staticmethod
    def delete_rows(old_data: DataFrame, table_model: classname, dbo: DbObject):
        f"""
        Remove a DataFrame of rows from the {table_model} database table.

        Parameters
        ----------
        old_data : DataFrame
            A list containing the entries you want to have removed from the target database table.
        table_model : classname
            The object model you want to target while deleting old_data from the target database table.
        dbo : DbObject
            Allows access to all methods and properties of the desired {dbo} DbObject.
        """
        print(f'Deleting {table_model.__tablename__} rows that do not exist in the newest data pull...')
        for row in old_data if not is_local else progress_bar(old_data):
            entry = table_model()
            table_cols = inspect(table_model).columns
            pk = inspect(table_model).primary_key[0].name
            [setattr(entry, col.name, getattr(row, col.name)) for col in table_cols]
            query = table_model.__table__.delete().where(getattr(table_model, pk) == getattr(entry, pk))
            dbo.sa_engine.execute(query)
