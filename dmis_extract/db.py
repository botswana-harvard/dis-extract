import pymssql
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from .private_settings import Lis as LisCredentials


class Db(object):
    def __init__(self, protocol_identifier, database):
        self.protocol_identifier = protocol_identifier.upper()
        self.database = database
        self.engine = create_engine('mssql+pymssql://{user}:{passwd}@{host}:{port}/{db}'.format(
            user=LisCredentials.user, passwd=LisCredentials.password,
            host=LisCredentials.host, port=LisCredentials.port,
            db=LisCredentials.name))
        self._dictionary_list = pd.DataFrame()
        self._dictionary_category = pd.DataFrame()
        self._dictionary = pd.DataFrame()
        self._protocol = pd.DataFrame()

    def read_table(self, sql, columns=None):
        with self.engine.connect() as conn, conn.begin():
            df = pd.read_sql_query(sql, conn)
        if columns:
            df.rename(columns=columns, inplace=True)
            df = df[list(columns.values())]
        return df

    def clean_df(self, df):
        df.fillna(value=np.nan, inplace=True)
        for column in list(df.select_dtypes(include=['datetime64[ns, UTC]']).columns):
            df[column] = df[column].astype('datetime64[ns]')
        return df

    def render_as_table(self, df, page, columns=None, rows_per_page=None):
        """Return a tuple of THEAD and TBODY."""
        rows_per_page = rows_per_page or 10
        page = int(page)
        start = rows_per_page * (page - 1)
        end = rows_per_page * page
        columns = columns or df.columns
        head = []
        body = []
        head.append('<tr>')
        for column in df.columns:
            head.append('<th>%s</th>' % column)
        head.append('</tr>')
        for item in df[start:end].itertuples():
            body.append('<tr>')
            for column in columns:
                body.append('<td>%s</td>' % getattr(item, column))
            body.append('</tr>')
        return ''.join(head), ''.join(body)

    @property
    def protocol(self):
        if self._protocol.empty:
            sql = """select DC905.*, DC900.PID_name from BHP.dbo.DC905Response as DC905
            LEFT JOIN BHP.dbo.DC900Response as DC900 on DC905.categoryID=DC900.PID"""
            columns = {
                'PID': 'identifier',
                'study_longname': 'title',
                'PID_name': 'category',
            }
            self._protocol = self.clean_df(self.read_table(sql, columns))
        return self._protocol

    @property
    def dictionary_list(self):
        if self._dictionary_list.empty:
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
            self._dictionary_list = self.read_table(sql, columns)
            self._dictionary_list['identifier'] = self._dictionary_list['identifier'].str.upper()
            self._dictionary_list['protocol'] = self._dictionary_list['protocol'].str.upper()
            # self._dictionary_list = self._dictionaries.apply()
        return self._dictionary_list

    @property
    def dictionary(self):
        if self._dictionary.empty:
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
            for identifier in self.dictionary_list.query('protocol == \'{}\''.format(self.protocol_identifier))['identifier']:
                try:
                    sql = "select * from {}.dbo.{}Dict".format(self.database, identifier)
                    df = self.read_table(sql, columns)
                    df['source'] = '{}.{}Dict'.format(self.database, identifier)
                    df['table_type'] = df['table_type'].map({0: 'header', 1: 'body'}.get)
                    df['enabled'] = df.apply(lambda row: True if row['enabled'].strip() == '' else False, axis=1)
                    df['enabled'] = df['enabled'].astype(bool)
                    df['field'] = df['field'].str.lower()
                    df['new_field'] = df.apply(lambda row: self.field_name(row['prompt']), axis=1)
                    df = df.replace('-9', np.nan)
                    df = df.replace('09/09/9999', np.nan)
                    self._dictionary = pd.concat([self._dictionary, df])
                except Exception as e:
                    if 'pymssql.ProgrammingError' in str(e):
                        print('{}Dict does not exist. Got {}'.format(identifier, str(e)))
                    else:
                        raise
            # self._dictionary_category = self._dictionaries.apply()
        return self._dictionary

    def field_name(self, name):
        name = name.replace(':', '').replace('?', '')
        return {
            'Visit Code': 'visit_code',
            'Clinician\'s initials': 'cinitials',
            'Site Code': 'site_code',
            'site code': 'site_code',
            'PARTICIPANT\'S NAME (FIRST-LAST)': 'name',
            'Protocol Number': 'protocol',
            'BHP Participant ID (BID)': 'subject_identifier',
            'PID': 'subject_identifier',
            'SeqID': 'sequence',
            'seqid': 'sequence',
            'Participant Initials (first - last)': 'initials',
            'Initials (F-L)': 'initials',
            'Initials': 'initials',
            'Date of Visit': 'report_date',
            'DATE PARTICIPANT SIGNED': 'report_date',
            'Date form being completed': 'report_date',
            'HEADERDATE': 'report_date',
            'Comments': 'comments',
            'Date Specimen Collected': 'drawn_datetime',
            'Date Specimen Drawn': 'drawn_datetime',
            'BHHRL Specimen Number': 'specimen_identifier',
            'Specify': 'other_specify',
            'Specify drug': 'rx_name',
            'Drug': 'rx_name',
            'RX code string': 'rx_code',
            'Relation to any study meds': 'rx_relation',
            'DX code string': 'dx_code',
            'Diagnosis Code': 'dx_code',
            'Diagnosis': 'dx_code',
            'SX code string': 'sx_code',
            'Symptom Code': 'sx_code',
            'Specify Symptom': 'sx_specify',
            'SX Body': 'sx_body_code',
            'Body Site': 'sx_body_code',
            'DX_ORG': 'dx_org_code',
            'Organism': 'dx_org_code',
            'DX Body': 'dx_body_code',
            'Dose Status': 'dose_status',
            'Dose/day (in mgs)': 'rx_dose',
            'Date Mod. Started': 'rx_mod_date',
            'Method': 'method',
            'Resolution': 'resolution',
            'Onset': 'onset',
            'Status': 'status',
            'Reason for Mod.': 'rx_mod_reason',
            'Specify reason for mod': 'rx_mod_reason_specify',
            'Toxicity Grading': 'grade',
            'Tox Grade': 'grade',
            'Grade': 'grade',
            'Age (years)': 'age_in_years',
            'How many children of your own do you have': 'children',
            'SAE Reference Number': 'sae_reference',
            'Has the dose status of any Study medication been modified since the scheduled visit': 'rx_dose_modified',
            'Does the Participant have any diagnoses relating to the primary reason ofr SAE (regardless of grade)': 'rx_relation',
            'Relation to any study meds': 'rx_relation',
        }.get(name, np.nan)
