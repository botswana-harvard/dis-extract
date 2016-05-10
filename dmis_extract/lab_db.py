import pandas as pd

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from .db import Db


class LabDb(Db):

    def __init__(self, protocol_identifier, database):
        self.received = pd.DataFrame()
        self.resulted = pd.DataFrame()
        self.stored = pd.DataFrame()
        super(LabDb, self).__init__(protocol_identifier, database)

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

    def fetch_received(self, days):
        modification_datetime = self.modification_datetime(days)
        sql = ('select PID, headerdate, PAT_ID, sample_protocolnumber, tid, sample_date_drawn, '
               'edc_specimen_identifier,sample_condition, KeyOpCreated, KeyOpLastModified, '
               'dateCreated, dateLastModified '
               'from BHPLAB.dbo.LAB01Response as L '
               'where sample_protocolnumber=\'{protocol_identifier}\' '
               'and dateLastModified>=\'{date_modified}\' '
               'ORDER BY L.dateLastModified desc').format(
                   protocol_identifier=self.protocol_identifier,
                   date_modified=modification_datetime.strftime('%Y-%m-%d 00:00:00.000'))
        columns = {
            'PID': 'receive_identifier',
            'headerdate': 'received_datetime',
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
        self.received = self.clean_df(self.read_table(sql, columns))

    def fetch_resulted(self, days, merge=None):
        merge = True if merge is None else merge
        modification_datetime = self.modification_datetime(days)
        sql = ('SELECT L.PID as receive_identifier, L21.PID as lis_identifier, reportdate, panel_id, sample_assay_date, utestid, result, result_quantifier, '
               'L21D.KeyOpCreated, L21D.KeyOpLastModified, '
               'L21D.dateCreated, L21D.dateLastModified, '
               'L.dateLastModified as receive_modified '
               'from BHPLAB.dbo.LAB01Response as L '
               'LEFT JOIN BHPLAB.dbo.LAB21Response as L21 on L.PID=L21.PID '
               'LEFT JOIN BHPLAB.dbo.LAB21ResponseQ001X0 as L21D on L21.Q001X0=L21D.QID1X0 '
               'where L.sample_protocolnumber=\'{protocol_identifier}\' '
               'and L21.dateLastModified>=\'{date_modified}\' '
               'and L21D.QID1X0 is not NULL '
               'ORDER BY L21D.dateLastModified').format(
                   protocol_identifier=self.protocol_identifier,
                   date_modified=modification_datetime.strftime('%Y-%m-%d 00:00:00.000'))
        columns = {
            'lis_identifier': 'lis_identifier',
            'receive_identifier': 'receive_identifier',
            'reportdate': 'report_datetime',
            'sample_assay_date': 'assay_datetime',
            'panel_id': 'panel_id',
            'result': 'result_value',
            'utestid': 'utestid',
            'result_quantifier': 'result_quantifier',
            'KeyOpCreated': 'user_created',
            'KeyOpLastModified': 'user_modified',
            'dateCreated': 'created',
            'dateLastModified': 'modified',
            'receive_modified': 'receive_modified',
        }
        self.resulted = self.clean_df(self.read_table(sql, columns))
        self.resulted['report_datetime'] = pd.to_datetime(
            self.resulted['report_datetime'], format='%d/%m/%Y').astype('datetime64[ns]')
        self.resulted['assay_datetime'] = pd.to_datetime(
            self.resulted['assay_datetime'], format='%d/%m/%Y').astype('datetime64[ns]')
        if merge:
            self.fetch_received(days=(date.today() - self.resulted['receive_modified'].min().date()).days)
            self.resulted = pd.merge(
                self.resulted, self.received,
                left_on='lis_identifier', right_on='receive_identifier',
                how='left', suffixes=['', '_recv'])
            self.resulted.drop(['receive_identifier_recv'], axis=1, inplace=True)

    def fetch_stored(self, days, merge=None):
        merge = True if merge is None else merge
        modification_datetime = self.modification_datetime(days)
        sql = ('SELECT ST305.PID as freezer_identifier, FREEZER_NAME, ST405.PID as rack_identifier, '
               'ST505D.*, ST505.PID as box_identifier, ST505.box_name, ST505.box_comment '
               'from BHPLAB.dbo.ST505ResponseQ001X0 as ST505D '
               'LEFT JOIN BHPLAB.dbo.ST505Response as ST505 on ST505D.QID1X0=ST505.Q001X0 '
               'left join BHPLAB.DBO.ST405ResponseQ001X0 as ST405D on ST505.PID=ST405D.BOX_ID '
               'left join BHPLAB.DBO.ST405Response as ST405 on ST405.Q001X0=ST405D.QID1X0 '
               'left join BHPLAB.DBO.ST305ResponseQ001X0 as ST305D on ST405.PID=ST305D.RACK_ID '
               'left join BHPLAB.DBO.ST305Response as ST305 on ST305.Q001X0=ST305D.QID1X0 '
               'where ST505D.sample_protocolnumber=\'{protocol_identifier}\' '
               'and ST505D.dateLastModified>=\'{date_modified}\' '
               'and ST505D.sample_id <> \'empty\' '
               'ORDER BY ST505D.dateLastModified').format(
                   protocol_identifier=self.protocol_identifier,
                   date_modified=modification_datetime.strftime('%Y-%m-%d 00:00:00.000'))
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
        self.stored = self.clean_df(self.read_table(sql, columns))
