from django.test.testcases import TestCase
from dmis_extract.db import Db
from pprint import pprint


class TestDb(TestCase):

    def test_connect(self):
        db = Db(database='BHPLAB')
        conn = db.engine.connect()
        result = conn.execute(
            "select count(*) as records from BHPLAB.dbo.LAB01Response")
        for row in result:
            self.assertGreater(row['records'], 0)
        conn.close()

    def test_read_table(self):
        db = Db(database='BHPLAB')

        sql = "select top 10 * from BHPLAB.dbo.LAB01Response"
        df = db.to_df(sql=sql, rename_columns=None)
        self.assertEqual(len(df), 10)

    def test_read_table_columns_lower(self):
        db = Db(database='BHPLAB')

        sql = "select top 10 * from BHPLAB.dbo.LAB01Response"
        df = db.to_df(sql=sql)
        self.assertIn('pid', list(df.columns))

    def test_read_table_rename_column(self):
        db = Db(database='BHPLAB')
        sql = "select top 10 * from BHPLAB.dbo.LAB01Response"
        df = db.to_df(sql=sql, rename_columns={
            'PID': 'specimen_identifier'})
        self.assertIn('specimen_identifier', list(df.columns))

    def test_read_table_columns_natural(self):
        db = Db(database='BHPLAB')
        sql = "select top 10 * from BHPLAB.dbo.LAB01Response"
        df = db.to_df(sql=sql, force_lower_columns=False)
        self.assertIn('PID', list(df.columns))
