from django.test.testcases import TestCase
from dmis_extract.lab_data import LabData


class TestLab(TestCase):

    def test_protocols(self):
        data = LabData(protocol_identifier='BHP066',
                       database='BHPLAB', limit=5)
        data.fetch_received(days=14)
