import pymssql
import pandas as pd

from django.core.management.color import color_style
from sqlalchemy import create_engine
from edc_pdutils import DfPrepper

from .private_settings import Lis as LisCredentials

style = color_style()


class Db(object):

    df_prepper_cls = DfPrepper

    def __init__(self, database=None):
        self.database = database
        self.engine = create_engine('mssql+pymssql://{user}:{passwd}@{host}:{port}/{db}'.format(
            user=LisCredentials.user, passwd=LisCredentials.password,
            host=LisCredentials.host, port=LisCredentials.port,
            db=LisCredentials.name))

    def to_df(self, sql, rename_columns=None, force_lower_columns=None):
        force_lower_columns = True if force_lower_columns is None else force_lower_columns
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql_query(sql, conn)
        if rename_columns:
            df.rename(columns=rename_columns, inplace=True)
        if force_lower_columns:
            columns = {col: col.lower() for col in list(df.columns)}
            df.rename(columns=columns, inplace=True)
        df = self.df_prepper_cls(
            dataframe=df, original_row_count=len(df.index))
        return df
