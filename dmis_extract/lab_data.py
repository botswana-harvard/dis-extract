import pandas as pd

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from .db import Db


class LabData:

    db_cls = Db

    def __init__(self, protocol_identifier, days=None, database=None, limit=None):
        self.db = self.db_cls(database=database)
        self.resulted_sql = None
        self.received_sql = None
        self.protocol_identifier = protocol_identifier
        self.days = days or -1
        self.received = pd.DataFrame()
        self.resulted = pd.DataFrame()
        self.stored = pd.DataFrame()
        self.limit = ''
        if limit:
            self.limit = f'top {limit}'

    def modification_datetime(self, days):
        days = -1 if days is None else days
        if days >= 0:
            modification_datetime = datetime.today() - relativedelta(days=days)
        else:
            modification_datetime = datetime(1900, 1, 1)
        return modification_datetime

    def received_condensed(self, days):
        if self.received.empty:
            self.fetch_received(days)
        return self.received[['receive_identifier', 'subject_identifier', 'received_datetime',
                              'test_id', 'drawn_datetime', 'specimen_condition', 'modified']]

    def fetch_received(self, days=None):
        days = days or self.days
        modification_datetime = self.modification_datetime(
            days).strftime('%Y-%m-%d 00:00:00.000')
        sql = (
            f'select {self.limit} PID, headerdate, PAT_ID, sample_protocolnumber, tid, sample_date_drawn, '
            f'edc_specimen_identifier,sample_condition, KeyOpCreated, KeyOpLastModified, '
            f'dateCreated, dateLastModified '
            f'from BHPLAB.dbo.LAB01Response as L ')
        where = (f'where L.dateLastModified>=\'{modification_datetime}\' ')
        if self.protocol_identifier.strip():
            where += (
                f' and L.sample_protocolnumber=\'{self.protocol_identifier}\' ')
        order = 'ORDER BY L.dateLastModified'
        sql = sql + where + order
        self.received_sql = sql
        columns = {
            'PID': 'receive_identifier',
            'headerdate': 'received_datetime',
            'edc_specimen_identifier': 'edc_specimen_identifier',
            'sample_date_drawn': 'drawn_datetime',
            'PAT_ID': 'subject_identifier',
            'tid': 'test_id',
            'sample_protocolnumber': 'protocol',
            'sample_condition': 'specimen_condition',
            'KeyOpCreated': 'user_created',
            'KeyOpLastModified': 'user_modified',
            'dateCreated': 'created',
            'dateLastModified': 'modified',
        }
        self.received = self.db.to_df(sql, columns)

    def fetch_resulted(self, days=None, merge=None):
        days = days or self.days
        merge = True if merge is None else merge
        modification_datetime = self.modification_datetime(
            days).strftime('%Y-%m-%d 00:00:00.000')
        sql = (
            f'SELECT {self.limit} L.PID as receive_identifier, '
            'L21.PID as lis_identifier, L.sample_protocolnumber as protocol, '
            'reportdate, l.tid, sample_assay_date, utestid, result, result_quantifier, '
            'L21D.KeyOpCreated, L21D.KeyOpLastModified, '
            'L21D.dateCreated, L21D.dateLastModified, '
            'L.dateLastModified as receive_modified '
            'from BHPLAB.dbo.LAB01Response as L '
            'LEFT JOIN BHPLAB.dbo.LAB21Response as L21 on L.PID=L21.PID '
            'LEFT JOIN BHPLAB.dbo.LAB21ResponseQ001X0 as L21D on L21.Q001X0=L21D.QID1X0 ')
        where = (f'where L.dateLastModified>=\'{modification_datetime}\' '
                 f'and L21D.QID1X0 is not NULL ')
        if self.protocol_identifier.strip():
            where += (
                f' and L.sample_protocolnumber=\'{self.protocol_identifier}\' ')
        order = 'ORDER BY L21D.dateLastModified'
        sql = sql + where + order
        self.resulted_sql = sql
        columns = {
            'protocol': 'protocol',
            'lis_identifier': 'lis_identifier',
            'receive_identifier': 'receive_identifier',
            'reportdate': 'report_datetime',
            'sample_assay_date': 'assay_datetime',
            'tid': 'panel_id',
            'result': 'result_value',
            'utestid': 'utestid',
            'result_quantifier': 'result_quantifier',
            'KeyOpCreated': 'user_created',
            'KeyOpLastModified': 'user_modified',
            'dateCreated': 'created',
            'dateLastModified': 'modified',
            'receive_modified': 'receive_modified',
        }
        self.resulted = self.db.to_df(sql, columns)
        self.resulted['report_datetime'] = pd.to_datetime(
            self.resulted['report_datetime'], infer_datetime_format=True, dayfirst=True)
        self.resulted['assay_datetime'] = pd.to_datetime(
            self.resulted['assay_datetime'], infer_datetime_format=True, dayfirst=True)
        if merge:
            self.fetch_received(
                days=(date.today() - self.resulted['receive_modified'].min().date()).days)
            self.resulted = pd.merge(
                self.resulted, self.received,
                left_on='lis_identifier', right_on='receive_identifier',
                how='left', suffixes=['', '_recv'])
            self.resulted.drop(['receive_identifier_recv'],
                               axis=1, inplace=True)

    def fetch_stored(self, days=None, merge=None):
        merge = True if merge is None else merge
        modification_datetime = self.modification_datetime(
            days).strftime('%Y-%m-%d 00:00:00.000')
        sql = (
            f'SELECT {self.limit} ST305.PID as freezer_identifier, FREEZER_NAME, ST405.PID as rack_identifier, '
            'ST505D.*, ST505.PID as box_identifier, ST505.box_name, ST505.box_comment '
            'from BHPLAB.dbo.ST505ResponseQ001X0 as ST505D '
            'LEFT JOIN BHPLAB.dbo.ST505Response as ST505 on ST505D.QID1X0=ST505.Q001X0 '
            'left join BHPLAB.DBO.ST405ResponseQ001X0 as ST405D on ST505.PID=ST405D.BOX_ID '
            'left join BHPLAB.DBO.ST405Response as ST405 on ST405.Q001X0=ST405D.QID1X0 '
            'left join BHPLAB.DBO.ST305ResponseQ001X0 as ST305D on ST405.PID=ST305D.RACK_ID '
            'left join BHPLAB.DBO.ST305Response as ST305 on ST305.Q001X0=ST305D.QID1X0 '
            f'where ST505D.sample_protocolnumber=\'{self.protocol_identifier}\' '
            f'and ST505D.dateLastModified>=\'{modification_datetime}\' '
            'and ST505D.sample_id <> \'empty\' '
            'ORDER BY ST505D.dateLastModified')
        columns = {
            'freezer_identifier': 'freezer_identifier',
            'FREEZER_NAME': 'freezer_name',
            'rack_identifier': 'rack_identifier',
            'box_identifier': 'box_identifier',
            'box_name': 'box_name',
            'box_comment': 'box_comment',
            'sample_id': 'aliquot_identifier',
            'sample_type': 'aliquot_type',
            'sample_protocolnumber': 'protocol',
            'box_row': 'row',
            'box_col': 'col',
            'sample_processing_status': 'aliquot_processing_status',
            'KeyOpCreated': 'user_created',
            'KeyOpLastModified': 'user_modified',
            'dateCreated': 'created',
            'dateLastModified': 'modified',
        }
        self.stored = self.db.to_df(sql, columns)
