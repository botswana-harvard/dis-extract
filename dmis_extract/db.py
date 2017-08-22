import sys
import pymssql
import pandas as pd
import numpy as np

from django.core.management.color import color_style
from sqlalchemy import create_engine

from .private_settings import Lis as LisCredentials

style = color_style()


class Db(object):
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
        return self.format_df(df=df)

    def format_df(self, df=None):
        df.fillna(value=np.nan, inplace=True)
        for column in list(df.select_dtypes(include=['datetime64[ns, UTC]']).columns):
            df[column] = df[column].astype('datetime64[ns]')
        return df


#     def field_name(self, name):
#         """field mappings."""
#         name = name.replace(':', '').replace('?', '')
#         return {
#             'Visit Code': 'visit_code',
#             'Clinician\'s initials': 'cinitials',
#             'Site Code': 'site_code',
#             'site code': 'site_code',
#             'PARTICIPANT\'S NAME (FIRST-LAST)': 'name',
#             'Protocol Number': 'protocol',
#             'BHP Participant ID (BID)': 'subject_identifier',
#             'PID': 'subject_identifier',
#             'SeqID': 'sequence',
#             'seqid': 'sequence',
#             'Participant Initials (first - last)': 'initials',
#             'Initials (F-L)': 'initials',
#             'Initials': 'initials',
#             'Date of Visit': 'report_date',
#             'DATE PARTICIPANT SIGNED': 'report_date',
#             'Date form being completed': 'report_date',
#             'HEADERDATE': 'report_date',
#             'Comments': 'comments',
#             'Date Specimen Collected': 'drawn_datetime',
#             'Date Specimen Drawn': 'drawn_datetime',
#             'BHHRL Specimen Number': 'specimen_identifier',
#             'Specify': 'other_specify',
#             'Specify drug': 'rx_name',
#             'Drug': 'rx_name',
#             'RX code string': 'rx_code',
#             'Relation to any study meds': 'rx_relation',
#             'DX code string': 'dx_code',
#             'Diagnosis Code': 'dx_code',
#             'Diagnosis': 'dx_code',
#             'SX code string': 'sx_code',
#             'Symptom Code': 'sx_code',
#             'Specify Symptom': 'sx_specify',
#             'SX Body': 'sx_body_code',
#             'Body Site': 'sx_body_code',
#             'DX_ORG': 'dx_org_code',
#             'Organism': 'dx_org_code',
#             'DX Body': 'dx_body_code',
#             'Dose Status': 'dose_status',
#             'Dose/day (in mgs)': 'rx_dose',
#             'Date Mod. Started': 'rx_mod_date',
#             'Method': 'method',
#             'Resolution': 'resolution',
#             'Onset': 'onset',
#             'Status': 'status',
#             'Reason for Mod.': 'rx_mod_reason',
#             'Specify reason for mod': 'rx_mod_reason_specify',
#             'Toxicity Grading': 'grade',
#             'Tox Grade': 'grade',
#             'Grade': 'grade',
#             'Age (years)': 'age_in_years',
#             'How many children of your own do you have': 'children',
#             'SAE Reference Number': 'sae_reference',
#             'Has the dose status of any Study medication been modified since the scheduled visit': 'rx_dose_modified',
#             'Does the Participant have any diagnoses relating to the primary reason ofr SAE (regardless of grade)': 'rx_relation',
#             'Relation to any study meds': 'rx_relation',
#         }.get(name, np.nan)

#     def render_as_html_table(self, df, page, columns=None, rows_per_page=None):
#         """Return a tuple of THEAD and TBODY."""
#         rows_per_page = rows_per_page or 10
#         page = int(page)
#         start = rows_per_page * (page - 1)
#         end = rows_per_page * page
#         columns = columns or df.columns
#         head = []
#         body = []
#         head.append('<tr>')
#         for column in df.columns:
#             head.append('<th>%s</th>' % column)
#         head.append('</tr>')
#         if len(df) == 0:
#             body = '<td colspan="{}">No records to display</td></tr>'.format(
#                 len(df.columns))
#         else:
#             for item in df[start:end].itertuples():
#                 body.append('<tr>')
#                 for column in columns:
#                     body.append('<td>%s</td>' % getattr(item, column))
#                 body.append('</tr>')
#         return ''.join(head), ''.join(body)
