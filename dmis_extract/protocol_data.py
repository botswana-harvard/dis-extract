import pandas as pd
import numpy as np

from .db import Db


class ProtocolData:

    db_cls = Db

    def __init__(self, **kwargs):
        self.db = self.db_cls(**kwargs)
        self._data_dictionaries = pd.DataFrame()
        self._data_dictionary = pd.DataFrame()
        self._protocol = pd.DataFrame()

    @property
    def protocols(self):
        if self._protocol.empty:
            sql = """select DC905.*, DC900.PID_name from BHP.dbo.DC905Response as DC905
            LEFT JOIN BHP.dbo.DC900Response as DC900 on DC905.categoryID=DC900.PID"""
            columns = {
                'PID': 'identifier',
                'study_longname': 'title',
                'PID_name': 'category',
            }
            self._protocol = self.db.to_df(sql=sql, rename_columns=columns)
        return self._protocol

    @property
    def data_dictionaries(self):
        if self._data_dictionaries.empty:
            sql = """select F0250.*, F0145.pid_name from BHP.dbo.F0250Response as F0250
            LEFT JOIN BHP.dbo.F0145Response as F0145 on F0250.FORM_CATEGORYID=F0145.PID"""
            columns = {
                'PID': 'dmis_id',
                'FORM_ID': 'identifier',
                'FORM_PROTOCOLNUMBER': 'protocol',
                'FORM_VERSION': 'form_version',
                'FORM_TITLE': 'title',
                'pid_name': 'category',
            }
            self._data_dictionaries = self.db.to_df(sql, columns)
            self._data_dictionaries['identifier'] = (
                self._data_dictionaries['identifier'].str.upper())
            self._data_dictionaries['protocol'] = (
                self._data_dictionaries['protocol'].str.upper())
        return self._data_dictionaries

    def get_data_dictionary(self, form_id=None):
        if self._data_dictionary.empty:
            columns = {
                'DATATYPE': 'data_type',
                'DEFAULTVALUE': 'default',
                'DICTTYPE': 'table_type',
                'FIELD': 'field',
                'KEYFIELD': 'foreign_key',
                'LENGTH': 'length',
                'PROMPT': 'prompt',
                'SHOWORDER': 'display_order',
                'TBL': 'table',
                'VERSION': 'version',
                'HTMLCONTROLENABLED': 'enabled',
            }
            cols = ','.join(list(columns.keys()))
            tbl = f'{self.db.database}.dbo.{form_id}Dict'
            sql = f'select {cols} from {tbl}'
            df = self.db.to_df(sql=sql, rename_columns=columns)
            df['source'] = tbl
            df['table_type'] = df['table_type'].map(
                {0: 'header', 1: 'body'}.get)
            df['enabled'] = df.apply(
                lambda row: True if row['enabled'].strip() == '' else False, axis=1)
            df['enabled'] = df['enabled'].astype(bool)
            df['field'] = df['field'].str.lower()
            df = df.replace('-9', np.nan)
            df = df.replace('09/09/9999', np.nan)
            self._data_dictionary = df
        return self._data_dictionary
